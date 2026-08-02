from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline_service import run_pipeline, get_rag_resources
from rag_embedder import retrieve
import llm_service
from llm_service import ContextMatch, LLMServiceError

app = FastAPI(
    title="Sözleşme Risk Analizörü API",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Document Memory Store
SESSION_MEMORY = {
    "ocr_text": "",
    "last_document_matches": []
}

@app.get("/")
def root():
    return {"message": "Sözleşme Risk Analizörü API çalışıyor."}

@app.get("/health")
def health():
    return {
        "api": "ok",
        "slm": llm_service.health_check(),
    }

def _matches_to_context(matches: list[dict], limit: int = 5) -> list[ContextMatch]:
    context = []
    for m in matches[:limit]:
        context.append(
            ContextMatch(
                eslesen_madde=m.get("eslesen_riskli_madde", m.get("belgedeki_madde", "")),
                validity=m.get("validity", ""),
                chain_of_thought=m.get("aciklama", ""),
            )
        )
    return context

@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    file_extension = Path(file.filename or "").suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Yalnızca PDF, JPG, JPEG veya PNG dosyaları yüklenebilir.",
        )

    file_path = UPLOAD_DIR / Path(file.filename).name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await file.close()

    pipeline_result = run_pipeline(str(file_path.resolve()))
    
    # SAVE DOCUMENT TEXT & MATCHES TO MEMORY
    SESSION_MEMORY["ocr_text"] = pipeline_result.get("ocr_text", "")
    SESSION_MEMORY["last_document_matches"] = pipeline_result.get("risk_matches", [])

    ai_summary = None
    ai_summary_error = None
    
    # Generate summary directly using extracted text or matches
    if SESSION_MEMORY["ocr_text"] or pipeline_result["risk_matches"]:
        try:
            summary_prompt = (
                "Aşağıda yüklenen sözleşmenin metni ve tespit edilen riskli maddeler yer almaktadır. "
                "Bu sözleşmeyi analiz ederek genel risk durumunu, önemli maddeleri ve dikkat edilmesi "
                "gereken noktaları 3-4 cümlelik sade bir Türkçe ile özetle:\n\n"
                f"Sözleşme Metni:\n{SESSION_MEMORY['ocr_text'][:2000]}\n\n"
            )
            ai_summary = llm_service.chat(
                summary_prompt,
                context=_matches_to_context(pipeline_result["risk_matches"]),
            )
        except LLMServiceError as exc:
            ai_summary_error = str(exc)

    return {
        "message": "Dosya başarıyla analiz edildi.",
        "filename": file_path.name,
        "ocr_text": pipeline_result["ocr_text"],
        "chunk_count": pipeline_result["chunk_count"],
        "risk_match_count": pipeline_result["risk_match_count"],
        "risk_matches": pipeline_result["risk_matches"],
        "ai_summary": ai_summary,
        "ai_summary_error": ai_summary_error,
    }

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Mesaj boş olamaz.")

    try:
        rag_index, rag_data = get_rag_resources()
        db_matches = retrieve(
            query_text=payload.message,
            index=rag_index,
            data=rag_data,
            top_k=3,
        )
    except FileNotFoundError:
        db_matches = []

    # Inject the uploaded document text into the chat query
    prompt_with_document = payload.message
    if SESSION_MEMORY["ocr_text"]:
        prompt_with_document = (
            f"Kullanıcının yüklediği belge metni:\n\"\"\"{SESSION_MEMORY['ocr_text'][:3000]}\"\"\"\n\n"
            f"Kullanıcının Sorusu: {payload.message}"
        )

    doc_matches_context = _matches_to_context(SESSION_MEMORY["last_document_matches"])
    db_matches_context = [
        ContextMatch(
            eslesen_madde=m["eslesen_madde"],
            validity=m.get("validity", ""),
            chain_of_thought=m.get("chain_of_thought", ""),
        )
        for m in db_matches
    ]
    
    combined_context = doc_matches_context + db_matches_context

    try:
        reply = llm_service.chat(prompt_with_document, context=combined_context)
    except LLMServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "reply": reply,
        "context_matches": [
            {
                "eslesen_madde": m["eslesen_madde"],
                "validity": m.get("validity", ""),
                "benzerlik_skoru": round(m.get("benzerlik_skoru", 0.0), 4),
            }
            for m in db_matches
        ],
    }