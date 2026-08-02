# LexVision Team

## Grup 115

## Takım Üyeleri

- Begüm Sude Bölükbaş
- Sudegül Bayram
- Tuğçe Temiz
- Enes Efe
- Hüseyin Emirhan Solak

---

# 📄 Legal AI Assistant (RAG)

Legal AI Assistant, Türkçe ticari sözleşmeler (ilk aşamada iş ve kira sözleşmeleri) üzerinde riskli maddeleri tespit etmek amacıyla geliştirilen Retrieval-Augmented Generation (RAG) tabanlı yapay zekâ destekli bir analiz sistemidir.

Sistem; kullanıcı tarafından yüklenen PDF veya görsel formatındaki sözleşmeleri OCR teknolojisi ile metne dönüştürmekte, metni madde bazında analiz ederek ilgili mevzuat ve emsal kararlarla karşılaştırmakta ve kullanıcıya riskli hükümleri açıklamalarıyla birlikte sunmaktadır.

---

# 🎯 Proje Amacı

Bu projenin amacı;

- Türkçe ticari sözleşmeleri otomatik analiz etmek
- Riskli maddeleri tespit etmek
- İlgili kanun maddeleri ve emsal kararlarla karşılaştırmak
- Risk seviyelerini belirlemek
- Risklerin nedenlerini açıklamak
- RAG mimarisi kullanarak kullanıcıya güvenilir hukuki analiz sunmaktır.

---

# 🚀 Özellikler

- PDF, JPG, JPEG ve PNG formatındaki sözleşmeleri destekleme
- Unlimited-OCR ile metin çıkarımı
- Clause-Based Chunking
- Embedding oluşturma
- FAISS tabanlı Vector Database
- Retrieval-Augmented Generation (RAG)
- Fine-Tuned Small Language Model
- Risk seviyesi belirleme
- Risk açıklaması oluşturma
- FastAPI Backend
- Web kullanıcı arayüzü
- Admin Paneli

---

# 🏗️ Sistem Mimarisi

```
PDF / JPG / PNG
        │
        ▼
┌─────────────────────┐
│ Unlimited OCR       │
└─────────┬───────────┘
          │
          ▼
Metin Normalizasyonu
          │
          ▼
Clause-Based Chunking
          │
          ▼
Embedding Modeli
          │
          ▼
FAISS Vector Database
          │
          ▼
Retriever (RAG)
          │
          ▼
Fine-Tuned Model
          │
          ▼
Risk Analizi
          │
          ▼
FastAPI Backend
          │
          ▼
Frontend 
```

---

# 📂 Proje Yapısı

```
.
├── Sprint1/
│   ├── daily_scrum.md
│   ├── ocr_test.md
│   ├── sprint_review.md
│   └── sprint_retrospective.md
│
├── Sprint2/
│   ├── daily_scrum.md
│   ├── embedding_and_chunking_test.md
│   ├── sprint_review.md
│   └── sprint_retrospective.md
│
├── Sprint3/
│   ├── daily_scrum.md
│   ├── sprint_review.md
│   └── sprint_retrospective.md
│
├── backend/
├── frontend/
├── README.md
```

---

# 🛠️ Kullanılan Teknolojiler

| Teknoloji | Kullanım Amacı |
|------------|----------------|
| Python | Backend geliştirme ve AI Pipeline |
| FastAPI | Backend API |
| React / Next.js | Web Arayüzü |
| Unlimited-OCR | OCR |
| Hugging Face | Embedding modelleri |
| FAISS | Vector Database |
| DeepSeek | Fine-Tuning ve Risk Analizi |
| SQLite | Doküman ve embedding depolama |
| Git & GitHub | Versiyon kontrolü |

---

# 📄 Desteklenen Dosya Formatları

- PDF
- JPG
- JPEG
- PNG

---

# 📊 Veri Seti

Projede;

- Türkçe iş sözleşmeleri
- Türkçe kira sözleşmeleri
- Sentetik hukuk verileri

kullanılmıştır.

Veri seti ilerleyen sürümlerde farklı ticari sözleşmeler ile genişletilecektir.

---

# 🔍 OCR Testleri

OCR işlemleri için Unlimited-OCR modeli tercih edilmiştir.

Test sonuçları:

- ✅ PDF sözleşmeleri başarıyla okunmuştur.
- ✅ JPG sözleşmeleri başarıyla okunmuştur.
- ✅ Türkçe karakterler doğru şekilde tanınmıştır.
- ✅ Madde numaraları korunmuştur.

Detaylı rapor:

```
Sprint1/ocr_test.md
```

---

# 📅 Sprint 1 Çıktıları

- Proje konusu belirlendi.
- Scrum görev dağılımı tamamlandı.
- GitHub reposu oluşturuldu.
- İlk veri setleri toplandı.
- OCR modeli araştırıldı ve test edildi.
- Product Backlog oluşturuldu.
- OCR doğrulama çalışmaları tamamlandı.

---

# 📅 Sprint 2 Çıktıları

- Clause-Based Chunking geliştirildi.
- Embedding modeli oluşturuldu.
- FAISS tabanlı Vector Database oluşturuldu.
- Fine-Tuning veri seti hazırlandı.
- Fine-Tuned model geliştirildi.
- Embedding ve Chunking testleri gerçekleştirildi.
- RAG altyapısı tamamlandı.

---

# 📅 Sprint 3 Çıktıları

- OCR, Embedding ve RAG Pipeline entegre edildi.
- FastAPI Backend geliştirildi.
- Frontend kullanıcı arayüzü tamamlandı.
- PDF yükleme sistemi geliştirildi.
- Admin paneli oluşturuldu.
- OCR → RAG → Risk Analizi uçtan uca çalışır hale getirildi.
- Sistem testleri tamamlandı.
- Demo Day sunumu gerçekleştirildi.

---

# 👥 Ekip

| Rol | Sorumluluk |
|------|------------|
| Product Owner | Proje planlama ve koordinasyon |
| Scrum Master | Scrum süreçlerinin yönetimi |
| Developer | OCR geliştirme |
| Developer | Chunking & Embedding |
| Developer | Backend & Frontend |
| Developer | RAG ve Model Entegrasyonu |

---

# 📈 Proje Durumu

🟢 **Demo Sürümü Tamamlandı**

Sprint 1, Sprint 2 ve Sprint 3 başarıyla tamamlanmıştır.

Legal AI Assistant;

- OCR
- Embedding
- FAISS
- RAG
- Fine-Tuned Model
- FastAPI
- Frontend

bileşenleri kullanılarak uçtan uca çalışan bir prototip olarak geliştirilmiştir.

Kullanıcı sisteme sözleşmesini yükleyebilmekte, riskli maddeleri analiz ettirebilmekte ve ilgili açıklamaları görüntüleyebilmektedir.

---

# 📚 Gelecek Çalışmalar

- Daha büyük hukuk veri setleri ile modeli geliştirmek
- Çoklu belge analizi desteği eklemek
- Explainable AI yaklaşımını geliştirmek
- Docker desteği
- Cloud deployment
- Performans optimizasyonları
- Daha kapsamlı mevzuat ve emsal karar veri tabanı entegrasyonu

---

Bu proje Scrum metodolojisi kullanılarak ekip çalışması kapsamında geliştirilmiştir.
