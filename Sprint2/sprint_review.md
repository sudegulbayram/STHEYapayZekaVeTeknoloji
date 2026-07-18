# Sprint 2 Review

**Sprint:** 2
**Tarih:** 19 Temmuz 2026
**Katılımcılar:** Tüm ekip

---

## Sprint Hedefi
Clause-Based Chunking'in geliştirilmesi, embedding oluşturulması, RAG pipeline'ının kurulması ve fine-tuned SLM'in hazır hale getirilmesi.

## Tamamlanan İşler

- ✅ Chunking ve embedding modülü tamamlandı
- ✅ FAISS ile vector embedding altyapısı kuruldu
- ✅ Fine-tuning için, en çok ihlal edilen 50 madde çerçevesinde ~200 örnekten oluşan veri seti oluşturuldu
- ✅ Model fine-tune edildi

## Tamamlanamayan İşler

- 🔄 Fine-tune edilen modelin performans testi henüz yapılmadı
- 🔄 RAG pipeline'ının uçtan uca entegrasyonu (SLM ile entegrasyon) devam ediyor

## Sprint Hedefine Ulaşma Durumu

Yüksek oranda ulaşıldı. Embedding/chunking altyapısı ve fine-tuning veri seti hedeflenen şekilde tamamlandı. RAG pipeline'ın uçtan uca test edilmesi Sprint3'te gerçekleşecek.

## Demo / Ürün Durumu

OCR, FAISS tabanlı embedding/chunking altyapısı ve fine-tune edilmiş model hazır durumda; uçtan uca çalışan bir demo henüz yok.