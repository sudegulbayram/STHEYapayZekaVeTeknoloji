from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pipeline_service import run_pipeline

app = FastAPI(
    title="Sözleşme Risk Analizörü API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def root():
    return {
        "message": "Sözleşme Risk Analizörü API çalışıyor."
    }

@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    file_extension = Path(file.filename or "").suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Yalnızca PDF, JPG, JPEG veya PNG dosyaları yüklenebilir.",
        )

    safe_filename = "".join(c for c in (file.filename or "file") if c.isalnum() or c in ('_', '.', '-'))
    if not safe_filename:
        safe_filename = "upload_file" + file_extension
        
    file_path = UPLOAD_DIR / safe_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file,buffer)
        await file.close()
    except Exception as e:
        return {
            "message": f"Dosya kaydedilemedi: {str(e)}",
            "filename": file.filename,
            "saved_path": ""
        }

    # Pipeline'ı çalıştırıp gerçek sonucu yakalıyoruz
    try:
        pipeline_result = run_pipeline(str(file_path.resolve()))
        
        # Eğer pipeline bir sözlük veya metin döndürüyorsa onu kullanıyoruz
        if isinstance(pipeline_result, dict):
            analysis_msg = pipeline_result.get("summary") or pipeline_result.get("text") or str(pipeline_result)
        elif pipeline_result:
            analysis_msg = f"Analiz Sonucu:\n{str(pipeline_result)}"
        else:
            analysis_msg = "Dosya başarıyla analiz edildi, ancak metin çıkarılamadı."
            
    except Exception as e:
        analysis_msg = f"Dosya yüklendi fakat analiz sırasında hata oluştu: {str(e)}"

    return {
        "message": analysis_msg,
        "filename": file_path.name,
        "saved_path": str(file_path),
    }