# SLM Entegrasyonu (Hukuk Danışmanı - Qwen2.5-3B LoRA)

Bu backend, `veribootcamp-model-finetune-v2` altında eğitilen fine-tuned SLM'i
**Ollama** üzerinden yerel olarak çağırır (`llm_service.py`). Böylece FastAPI
süreci torch/unsloth/bitsandbytes gibi GPU'ya bağımlı ağır kütüphaneleri
yüklemek zorunda kalmaz — sadece basit bir HTTP isteği atar.

## 1) Ollama'yı kurun

https://ollama.com/download

## 2) Taban modeli indirin

```bash
ollama pull qwen2.5:3b-instruct
```

## 3) Eğitilmiş LoRA'yı GGUF'a çevirin

Bu depoda LoRA adaptörünün ağırlıkları (`adapter_model.safetensors`) bir
Git LFS işaretçisi olarak geldi; gerçek ağırlıkları içermiyor. Kendi eğitim
makinenizde (GPU + unsloth kurulu ortamda), `veribootcamp-model-finetune-v2`
klasöründe:

```bash
python export_gguf.py
```

Bu komut `output/hukuk_model_gguf/*-lora.gguf` dosyasını üretir ve varsa
otomatik olarak `backend/hukuk_model_lora.gguf` konumuna kopyalar (aynı
işlemi `local finetune.py` script'inin son adımı da eğitim sırasında zaten
yapar).

## 4) Ollama modelini oluşturun

```bash
cd backend
ollama create hukuk-danismani-slm -f Modelfile
```

## 5) Ollama'yı ayakta tutun

```bash
ollama serve
```

## 6) Backend'i başlatın

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Gerekirse ortam değişkenleriyle model adını / Ollama adresini özelleştirin:

```bash
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=hukuk-danismani-slm
```

## Uçlar

- `GET /health` → Ollama'ya ulaşılabiliyor mu, model yüklü mü kontrolü.
- `POST /upload` → Belge/görsel analiz eder, riskli madde eşleşmelerine ek
  olarak SLM'den üretilen `ai_summary` alanını döner.
- `POST /chat` → `{"message": "..."}` ile serbest soru-cevap; RAG'den
  bulunan ilgili madde örnekleri SLM'e bağlam olarak verilir.

## Ollama olmadan test etmek isterseniz

`llm_service.py`, Ollama'ya ulaşamadığında `LLMServiceError` fırlatır;
`/upload` bu durumda `ai_summary: null` ve `ai_summary_error` alanıyla
riskli madde analizini yine de döner, `/chat` ise `503` yanıtı verir.
Yani SLM ayakta değilken bile OCR + RAG pipeline'ı çalışmaya devam eder.
