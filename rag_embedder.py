import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


MODEL_NAME = "newmindai/Mursit-Large-TR-Retrieval"
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def build_index(data_path, index_path="rag_index.faiss"):

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Maddeleri al
    texts = [entry["clause_text"] for entry in data]
    
    # Tüm maddeleri embed et
    print(f"[BİLGİ] {len(texts)} madde embed ediliyor...")
    embeddings = get_model().encode(texts, convert_to_numpy=True)
    
    # Normalize et
    faiss.normalize_L2(embeddings)
    
    # FAISS index oluştur
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) 
    index.add(embeddings)

    faiss.write_index(index, index_path)
    
    print(f"[BAŞARILI] FAISS index oluşturuldu. {index.ntotal} madde eklendi.")
    return index, data

def load_index(index_path, data_path):
    index = faiss.read_index(index_path)
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return index, data

def retrieve(query_text, index, data, top_k=3):
    # Arama sorgusunu embed et
    query_embedding = get_model().encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    # Arama yap ve en benzer maddeleri al
    scores, indices = index.search(query_embedding, top_k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        entry = data[idx]
        results.append({
            "eslesen_madde": entry["clause_text"],
            "validity": entry.get("validity", "Geçersiz"),
            "chain_of_thought": entry.get("chain_of_thought", ""),
            "benzerlik_skoru": float(score)
})
    
    results = [r for r in results if r["benzerlik_skoru"] > 0.5]


    return results
