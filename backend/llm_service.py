"""
llm_service.py
---------------
Fine-tune edilmiş SLM (Small Language Model) için cikarim (inference) katmani.

Model: Qwen2.5-3B-Instruct + LoRA ("hukuk_model_lora")
Egitim script'i (`local finetune.py`) modeli GGUF formatinda disa aktarip
("output/hukuk_model_gguf") Ollama uzerinde calistirmayi ongordugu icin bu
servis de ayni yolu izler: SLM, Ollama uzerinden yerel olarak servis edilir.
Backend sureci bu sayede torch/unsloth/bitsandbytes gibi agir GPU
bagimliliklarini yuklemek zorunda kalmaz; sadece Ollama'nin HTTP API'sine
istek atar.

Kurulum (bkz. backend/README_LLM.md):
    1) Egitilmis LoRA'yi GGUF'a cevirin (finetune script'inin son adimi,
       ya da `python export_gguf.py`).
    2) `ollama create hukuk-danismani-slm -f Modelfile`
    3) Ollama servisini calisir durumda birakin (`ollama serve`).
    4) Backend'i baslatmadan once gerekirse OLLAMA_HOST / OLLAMA_MODEL
       ortam degiskenlerini ayarlayin.

Ollama kurulu/calismiyorsa bu modul hata firlatmaz; `LLMServiceError`
uzerinden anlamli bir mesajla basarisiz olur ve API katmani bunu kullaniciya
duzgun bir sekilde iletir.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Optional, List

import httpx

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hukuk-danismani-slm")
# Serbest sohbet için TABAN modeli kullanıyoruz (LoRA değil). LoRA, 2500
# örnekli tek-şablonlu (madde -> Geçerli/Geçersiz) veri setine güçlü şekilde
# uyum sağladığı için genel sohbette konudan bağımsız halüsinasyonlar
# üretip her girdiyi zorla kendi şablonuna oturtuyor. Bu yüzden:
#   - analyze_clause() -> OLLAMA_MODEL (fine-tuned LoRA, tek görev: madde analizi)
#   - chat()           -> OLLAMA_CHAT_MODEL (taban model, genel soru-cevap)
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b-instruct")
REQUEST_TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "500"))

# Egitimde kullanilan sistem prompt'u ile birebir ayni tutulmali; aksi halde
# LoRA'nin ogrendigi davranis kalibi (Gecerli/Gecersiz + gerekce) bozulur.
CLAUSE_SYSTEM_PROMPT = (
    "Sen uzman bir sözleşme danışmanısın. Verilen sözleşme maddesini hukuki "
    "olarak analiz et ve Geçerli/Geçersiz olduğuna karar ver."
)

# Serbest sohbet / dokuman analizi sonrasi genel soru-cevap icin, RAG
# baglamini da iceren daha genis bir sistem prompt'u.
CHAT_SYSTEM_PROMPT = (
    "Sen 'YZVT Hukuk Asistanı' adlı, Türk hukuku konusunda eğitilmiş bir "
    "yapay zeka danışmanısın. Kullanıcının sorularını, sana verilen bağlam "
    "(benzer riskli/geçerli madde örnekleri) ışığında, net ve kısa şekilde "
    "yanıtla. Emin olmadığın konularda bunu açıkça belirt ve bir hukuk "
    "uzmanına danışılmasını öner."
)


class LLMServiceError(RuntimeError):
    """Ollama'ya ulaşılamadığında ya da model yanıt üretemediğinde fırlatılır."""


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ContextMatch:
    """RAG'den gelen bir bağlam parçası (retrieve() çıktısıyla uyumlu)."""

    eslesen_madde: str
    validity: str = ""
    chain_of_thought: str = ""


def _build_context_block(matches: Iterable[ContextMatch]) -> str:
    lines = []
    for i, m in enumerate(matches, start=1):
        cot = m.chain_of_thought.strip() if isinstance(m.chain_of_thought, str) else ""
        block = (
            f"[{i}] Benzer madde: \"{m.eslesen_madde}\"\n"
            f"    Durum: {m.validity or 'Bilinmiyor'}\n"
        )
        if cot:
            block += f"    Gerekçe: {cot}\n"
        lines.append(block)
    return "\n".join(lines) if lines else "(İlgili bağlam bulunamadı.)"


def _ollama_chat(messages: List[dict], *, model: str, temperature: float = 0.2, max_tokens: int = 400) -> str:
    """Ollama /api/chat uç noktasına senkron istek atar ve model cevabını döner."""

    url = f"{OLLAMA_HOST.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.ConnectError as exc:
        raise LLMServiceError(
            "SLM sunucusuna (Ollama) ulaşılamadı. 'ollama serve' çalışıyor mu "
            f"kontrol edin. (host: {OLLAMA_HOST})"
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise LLMServiceError(
            f"SLM sunucusu hata döndürdü ({exc.response.status_code}): "
            f"model '{model}' mevcut mu? ('ollama list' ile kontrol edin, gerekirse "
            f"'ollama pull {model}' ya da 'ollama create {model} -f Modelfile' çalıştırın)"
        ) from exc
    except httpx.TimeoutException as exc:
        raise LLMServiceError("SLM yanıt süresi aşıldı (timeout).") from exc

    message = data.get("message", {})
    content = (message.get("content") or "").strip()

    if not content:
        raise LLMServiceError("SLM boş yanıt döndürdü.")

    return content


def analyze_clause(clause_text: str, context: Optional[Iterable[ContextMatch]] = None) -> str:
    """Tek bir sözleşme maddesini fine-tune edilmiş SLM ile analiz eder.

    `context`, RAG'den gelen benzer madde eşleşmelerini (chain-of-thought
    dahil) modele referans olarak verir; bu sayede model kendi ürettiği
    gerekçeyi eğitim verisindeki emsallerle tutarlı hale getirir.
    """

    user_content = f"Sözleşme Maddesi: {clause_text.strip()}"

    if context:
        user_content += (
            "\n\nBenzer emsal maddeler (RAG bağlamı):\n"
            + _build_context_block(context)
        )

    messages = [
        {"role": "system", "content": CLAUSE_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    return _ollama_chat(messages, model=OLLAMA_MODEL, temperature=0.2, max_tokens=350)


def chat(message: str, context: Optional[Iterable[ContextMatch]] = None,
         history: Optional[Iterable[ChatMessage]] = None) -> str:
    """Serbest sohbet / genel soru-cevap için SLM çağrısı (RAG destekli)."""

    messages: List[dict] = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]

    for h in history or []:
        messages.append({"role": h.role, "content": h.content})

    user_content = message.strip()
    if context:
        user_content += "\n\nBağlam (benzer maddeler):\n" + _build_context_block(context)

    messages.append({"role": "user", "content": user_content})

    return _ollama_chat(messages, model=OLLAMA_CHAT_MODEL, temperature=0.4, max_tokens=500)


def health_check() -> dict:
    """Ollama'nın ayakta olup olmadığını ve modelin yüklü olup olmadığını kontrol eder."""

    url = f"{OLLAMA_HOST.rstrip('/')}/api/tags"
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
    except Exception as exc:  # noqa: BLE001 - health check, her hatayi yutup raporla
        return {"ollama_reachable": False, "model_loaded": False, "error": str(exc)}

    model_loaded = any(OLLAMA_MODEL in name for name in models)
    chat_model_loaded = any(OLLAMA_CHAT_MODEL in name for name in models)
    return {
        "ollama_reachable": True,
        "model_loaded": model_loaded,
        "expected_model": OLLAMA_MODEL,
        "chat_model_loaded": chat_model_loaded,
        "expected_chat_model": OLLAMA_CHAT_MODEL,
        "available_models": models,
    }
