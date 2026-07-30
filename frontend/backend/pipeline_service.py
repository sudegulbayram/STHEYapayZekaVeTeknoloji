from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag_ingestion_pipeline import run_pipeline as original_run_pipeline


def run_pipeline(image_path: str) -> str:
    source_path = Path(image_path).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Yüklenen dosya bulunamadı: {source_path}")

    relative_path = source_path.relative_to(PROJECT_ROOT)

    # Orijinal pipeline'ı çalıştırıyoruz ve sonucunu yakalayıp döndürüyoruz
    result = original_run_pipeline(str(relative_path))
    
    # Eğer orijinal pipeline sonuç dönüyorsa onu döndür, dönmüyorsa başarılı mesajı ver
    if result:
        return str(result)
    return "Görsel başarıyla işlendi ve RAG veritabanına aktarıldı."