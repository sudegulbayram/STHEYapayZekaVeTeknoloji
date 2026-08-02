"""
export_gguf.py
---------------
"output/hukuk_model_lora" altindaki egitilmis LoRA adaptorunu GGUF formatina
cevirir (Ollama'da calistirmak icin). "local finetune.py" script'inin son
adimiyla ayni islemi, egitimi tekrar etmeden, mevcut bir checkpoint uzerinde
calistirmak icin ayri bir script olarak sunulmustur.

Kullanim:
    python export_gguf.py

Cikti:
    output/hukuk_model_gguf/*-lora.gguf

Ardindan bu dosyayi backend/Modelfile'in yanina "hukuk_model_lora.gguf"
adiyla kopyalayip 'ollama create hukuk-danismani-slm -f backend/Modelfile'
komutunu calistirin.
"""

import shutil
import sys
from pathlib import Path

from unsloth import FastLanguageModel

LORA_PATH = "output/hukuk_model_lora"
GGUF_OUTPUT_DIR = "output/hukuk_model_gguf"
BACKEND_MODELFILE_DIR = Path(__file__).resolve().parent.parent.parent / "STHEYapayZekaVeTeknoloji-main" / "backend"


def main() -> None:
    if not Path(LORA_PATH).exists():
        print(f"[HATA] LoRA klasoru bulunamadi: {LORA_PATH}")
        print("Once fine-tuning egitimini tamamlayin ('local finetune.py').")
        sys.exit(1)

    print(f"[1/2] {LORA_PATH} yukleniyor ve GGUF'a cevriliyor...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=LORA_PATH,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )

    # Sadece LoRA katmanlarini GGUF'a gomuyoruz (taban model Ollama'da zaten
    # "qwen2.5:3b-instruct" olarak mevcut olacak).
    model.save_pretrained_gguf(GGUF_OUTPUT_DIR, tokenizer, save_method="lora")

    gguf_files = sorted(Path(GGUF_OUTPUT_DIR).glob("*lora*.gguf"))
    if not gguf_files:
        print(f"[HATA] GGUF dosyasi olusturulamadi, '{GGUF_OUTPUT_DIR}' klasorunu kontrol edin.")
        sys.exit(1)

    gguf_file = gguf_files[0]
    print(f"[BAŞARILI] GGUF adaptörü oluşturuldu: {gguf_file}")

    if BACKEND_MODELFILE_DIR.exists():
        target = BACKEND_MODELFILE_DIR / "hukuk_model_lora.gguf"
        print(f"[2/2] {target} konumuna kopyalanıyor...")
        shutil.copy(gguf_file, target)
        print(
            "[BİTTİ] Şimdi çalıştırın:\n"
            f"  cd {BACKEND_MODELFILE_DIR}\n"
            "  ollama create hukuk-danismani-slm -f Modelfile\n"
            "  ollama serve"
        )
    else:
        print(
            "[UYARI] Backend klasörü otomatik bulunamadı. GGUF dosyasını "
            "elle 'backend/hukuk_model_lora.gguf' olarak kopyalayın."
        )


if __name__ == "__main__":
    main()
