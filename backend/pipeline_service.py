from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag_ingestion_pipeline import run_pipeline as original_run_pipeline

from rag_embedder import load_index, retrieve
from legal_chunker import parse_legal_text, flatten_chunks


RAG_INDEX_PATH = PROJECT_ROOT / "rag_index.faiss"
RAG_DATA_PATH = PROJECT_ROOT / "rag_data.json"

_rag_index = None
_rag_data = None


def get_rag_resources():
    global _rag_index, _rag_data

    if _rag_index is None or _rag_data is None:
        if not RAG_INDEX_PATH.exists():
            raise FileNotFoundError(f"FAISS index bulunamadı: {RAG_INDEX_PATH}")

        if not RAG_DATA_PATH.exists():
            raise FileNotFoundError(f"RAG veri dosyası bulunamadı: {RAG_DATA_PATH}")

        _rag_index, _rag_data = load_index(
            str(RAG_INDEX_PATH),
            str(RAG_DATA_PATH),
        )

    return _rag_index, _rag_data



def run_pipeline(image_path: str) -> dict:
    source_path = Path(image_path).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Yüklenen dosya bulunamadı: {source_path}")

    relative_path = source_path.relative_to(PROJECT_ROOT)

    # OCR ve hukuki metin parçalama işlemini çalıştırır.
    original_run_pipeline(str(relative_path))

    raw_text_path = PROJECT_ROOT / "ocr_ham_metin.txt"

    if not raw_text_path.exists():
        raise RuntimeError("OCR metin çıktısı oluşturulamadı.")

    ocr_text = raw_text_path.read_text(encoding="utf-8")

    # OCR metnini yeniden yapılandırılmış hukuki parçalara ayırır.
    root_node = parse_legal_text(ocr_text)
    document_chunks = flatten_chunks(root_node)

    # Hazır FAISS indexini ve riskli madde verilerini yükler.
    rag_index, rag_data = get_rag_resources()

    risk_matches = []
    seen_matches = set()

    # Belgedeki her parçayı FAISS veri tabanında arar.
    for chunk in document_chunks:
        matches = retrieve(
            query_text=chunk["text"],
            index=rag_index,
            data=rag_data,
            top_k=3,
        )

        for match in matches:
            matched_clause = match["eslesen_madde"]

            # Aynı riskli maddeyi cevapta tekrar göstermemek için.
            if matched_clause in seen_matches:
                continue

            seen_matches.add(matched_clause)

            risk_matches.append({
                "belgedeki_madde": chunk["text"],
                "madde_turu": chunk["metadata"]["clause_type"],
                "eslesen_riskli_madde": matched_clause,
                "validity": match["validity"],
                "aciklama": match["chain_of_thought"],
                "benzerlik_skoru": round(match["benzerlik_skoru"], 4),
            })

    # En güçlü benzerlikleri önce gösterir.
    risk_matches.sort(
        key=lambda item: item["benzerlik_skoru"],
        reverse=True,
    )

    return {
        "ocr_text": ocr_text,
        "chunk_count": len(document_chunks),
        "risk_match_count": len(risk_matches),
        "risk_matches": risk_matches[:10],
    }