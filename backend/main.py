from pathlib import Path
import shutil


from fastapi import FastAPI, File, HTTPException, UploadFile

from pipeline_service import run_pipeline


app = FastAPI(
    title="Sözleşme Risk Analizörü API",
    version="1.0.0",
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

    file_path = UPLOAD_DIR / Path(file.filename).name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await file.close()

    pipeline_result = run_pipeline(str(file_path.resolve()))

    return {
    "message": "Dosya başarıyla analiz edildi.",
    "filename": file_path.name,
    "ocr_text": pipeline_result["ocr_text"],
    "chunk_count": pipeline_result["chunk_count"],
    "risk_match_count": pipeline_result["risk_match_count"],
    "risk_matches": pipeline_result["risk_matches"],
}
