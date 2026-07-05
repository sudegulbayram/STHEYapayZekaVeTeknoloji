# Takım İsmi

Grup 115 

# Takım Üyeleri

-Begüm Sude Bölükbaş
-Sudegül Bayram
-Tuğçe Temiz
-Enes Efe
-Hüseyin Emirhan Solak

# 📄 Contract Risk Analyzer (RAG)

Türkçe ticari sözleşmelerde (ilk aşamada **iş sözleşmeleri** ve **kira sözleşmeleri**) yer alan riskli maddeleri tespit etmek amacıyla geliştirilen **Retrieval-Augmented Generation (RAG)** tabanlı yapay zekâ projesidir.

Sistem, yüklenen sözleşmeleri OCR ile okuyarak madde bazlı analiz eder ve kullanıcıya olası riskleri, risk seviyelerini ve açıklamalarını sunmayı hedeflemektedir.

---

# 🎯 Proje Amacı

Bu projenin amacı;

- Türkçe ticari sözleşmeleri analiz etmek,
- Riskli maddeleri otomatik olarak tespit etmek,
- Risk seviyelerini belirlemek,
- Risklerin nedenlerini açıklamak,
- Gelecekte güvenli alternatif maddeler önerebilen bir RAG sistemi geliştirmektir.

---

# 🚀 Özellikler

- PDF ve görsel (JPG, PNG) formatındaki sözleşmeleri destekleme
- OCR ile metin çıkarımı
- Madde bazlı (Clause-Based) Chunking
- Embedding oluşturma
- Vector Database üzerinde benzer madde arama
- RAG mimarisi ile risk analizi
- Risk seviyesi belirleme
- Risk açıklaması oluşturma

---

# 🏗️ Proje Mimarisi

```text
PDF / JPG / PNG
       │
       ▼
 ┌───────────┐
 │    OCR    │ ◄─── (Custom Pipeline / Unlimited-OCR Benchmark)
 └─────┬─────┘
       │
       ▼
 Metin Çıkarma & Normalizasyon
       │
       ▼
 Clause-Based Chunking
       │
       ▼
 Embeddings (Hugging Face)
       │
       ▼
 Vector Database (Vektör Veri Tabanı)
       │
       ▼
 ┌─────────────────────────────────────────┐
 │            DeepSeek API                 │
 ├────────────────────┬────────────────────┤
 │  Generation Mode   │   Reasoning Mode   │
 │ (Sentetik Veri)    │   (CoT Risk Analizi)   │
 └────────────────────┴────────────────────┘
       │
       ▼
   Risk Analizi & Açıklama Çıktısı
```

---

# 📂 Proje Yapısı

```text
.
├── Sprint1/
│   ├── product_backlog.md
│   ├── sprint_review.md
│   ├── sprint_retrospective.md
│   └── ocr_test.md
│
├── src/
│   ├── data/
│   ├── ocr/
│   ├── chunking/
│   ├── rag/
│   └── models/
│
└── README.md
```

---

# 🛠️ Kullanılan Teknolojiler

| Teknoloji / Araç | Projedeki Rolü ve Kullanım Amacı |
|------------|------|
| Python | Projenin ana geliştirme dili; veri işleme pipeline'ları ve backend servislerinin yönetimi |
| OCR | Doküman türüne göre optimize edilmiş Custom OCR Pipeline ve Unlimited-OCR hibrit yapısı |
| RAG | Doküman tabanlı bilgi getirme altyapısı (Sprint 2'de belirlenecek kütüphaneler ile entegre edilecek). |
| DeepSeek (Generation Mode) | Veri kümesini genişletmek amacıyla yüksek kaliteli sentetik veri üretimi. |
| DeepSeek (Reasoning Mode) | Adım adım Chain of Thought (CoT) analizi. |
| Hugging Face | Açık kaynaklı modellerin/embedding süreçlerinin barındırılması ve entegrasyonu. |
| Git & GitHub | Kod tabanı yönetimi, sürüm kontrolü ve ekip içi iş birliği. |

---

# 📄 Desteklenen Dosya Formatları

- PDF
- JPG
- JPEG
- PNG

---

# 📊 Veri Seti

İlk sprint kapsamında;

- Türkçe kira sözleşmeleri
- Türkçe iş sözleşmeleri

toplanmaya başlanmıştır.

Veri seti ilerleyen sprintlerde farklı ticari sözleşmeler ile genişletilecektir.

---

# 🔍 OCR Testi

OCR işlemleri için **Unlimited-OCR (Baidu)** modeli tercih edilmiştir.

İlk testlerde;

- ✅ PDF sözleşmeleri başarıyla okunmuştur.
- ✅ JPG sözleşmeleri başarıyla okunmuştur.
- ✅ Türkçe karakterler doğru şekilde tanınmıştır.
- ✅ Madde numaraları korunmuştur.

Detaylı rapor için:

```
Sprint1/ocr_test.md
```

---

# 📅 Sprint 1 Çıktıları

Sprint 1 kapsamında;

- Proje konusu belirlendi.
- Scrum görev dağılımı tamamlandı.
- GitHub reposu oluşturuldu.
- İlk veri setleri toplandı.
- OCR modeli araştırıldı ve test edildi.
- OCR doğrulama çalışmaları tamamlandı.
- Product Backlog oluşturuldu.

---

# 📌 Sprint 2 Hedefleri

- Clause-Based Chunking geliştirilmesi
- Embedding oluşturulması
- Vector Database entegrasyonu
- RAG Pipeline oluşturulması
- Risk analizi prototipinin geliştirilmesi

---

# 👥 Ekip

| Rol | Sorumluluk |
|------|------------|
| Project Manager | Proje planlama ve koordinasyon |
| Scrum Master | Scrum süreçlerinin yönetimi |
| Developer | Veri toplama ve ön işleme |
| Developer | OCR ve Chunking |
| Developer | RAG ve Model Entegrasyonu |

---

# 📈 Proje Durumu

🟡 **Geliştirme Aşamasında**

Sprint 1 başarıyla tamamlanmıştır.

Şu anda OCR doğrulama süreci tamamlanmış olup Clause-Based Chunking geliştirme aşamasına geçilmektedir.

---

# 📚 Gelecek Çalışmalar

- Daha büyük Türkçe sözleşme veri seti oluşturulması
- Daha karmaşık OCR senaryolarının test edilmesi
- Risk açıklamalarının geliştirilmesi
- Güvenli alternatif madde önerileri
- Web arayüzünün geliştirilmesi

---

> Bu proje, Scrum metodolojisi kullanılarak ekip çalışması kapsamında geliştirilmektedir.
