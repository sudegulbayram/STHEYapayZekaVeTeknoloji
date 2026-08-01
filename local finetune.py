import os
import torch
from datasets import load_dataset
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from trl import SFTTrainer, SFTConfig

# ----------------------------------------------------------------------
# 1. TEMEL AYARLAR VE MODEL SEÇİMİ
# ----------------------------------------------------------------------
max_seq_length = 2048 
dtype = None 
load_in_4bit = True 

# Qwen 2.5 3B modeli seçildi (İndirme takılmasını önlemek için yerel klasörden okutuyoruz)
model_name = "./unsloth"

print(f"\n[1/6] {model_name} modeli 4-bit (QLoRA) formatında indiriliyor/yükleniyor...")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# ----------------------------------------------------------------------
# 2. LORA ADAPTÖRÜ KONFİGÜRASYONU
# ----------------------------------------------------------------------
print("\n[2/6] LoRA Adaptörleri ayarlanıyor...")

model = FastLanguageModel.get_peft_model(
    model,
    r = 16, 
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"], 
    lora_alpha = 16,
    lora_dropout = 0, 
    bias = "none",
    use_gradient_checkpointing = "unsloth", 
    random_state = 3407,
)

# ----------------------------------------------------------------------
# 3. VERİ SETİNİ YÜKLEME VE QWEN ŞABLONUNA ÇEVİRME
# ----------------------------------------------------------------------
print("\n[3/6] Veri seti yükleniyor ve Qwen formatına çevriliyor...")

# Şablon Llama'dan Qwen-2.5'e güncellendi
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "qwen-2.5", 
)

def formatting_prompts_func(examples):
    convos = examples["messages"]
    texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in convos]
    return {"text": texts}

dataset = load_dataset("json", data_files={"train": "fine_tuning_dataset_large.jsonl"}, split="train")
dataset = dataset.map(formatting_prompts_func, batched = True)

# ----------------------------------------------------------------------
# 4. EĞİTİM (TRAINING) PARAMETRELERİ
# ----------------------------------------------------------------------
print("\n[4/6] Eğitim başlıyor...")

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, 
    args = SFTConfig(
        per_device_train_batch_size = 4, # 16GB VRAM kapasitesi için 4'e çıkarıldı
        gradient_accumulation_steps = 4, 
        warmup_steps = 5,
        num_train_epochs = 3, # max_steps yerine daha esnek olan epoch yapısına geçildi
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(), 
        logging_steps = 1,
        optim = "adamw_8bit", 
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "output/checkpoints",
    ),
)

trainer_stats = trainer.train()

# ----------------------------------------------------------------------
# 5. MODELİ (LORA ADAPTÖRÜNÜ) KAYDETME
# ----------------------------------------------------------------------
print("\n[5/6] Eğitim tamamlandı! LoRA adaptörleri kaydediliyor...")

save_path = "output/hukuk_model_lora"
model.save_pretrained(save_path) 
tokenizer.save_pretrained(save_path)

# ----------------------------------------------------------------------
# 6. OLLAMA / GGUF FORMATINDA DIŞA AKTARMA (LORA)
# ----------------------------------------------------------------------
print("\n[6/6] LoRA adaptörü GGUF formatına dönüştürülüyor...")

# İndirme takılmasını önlemek adına sadece eğittiğimiz kısmı (LoRA) GGUF yapıyoruz
model.save_pretrained_gguf("output/hukuk_model_gguf", tokenizer, save_method="lora")

print("\n[BAŞARILI] İşlem tamam! 'output/hukuk_model_gguf' klasöründeki '-lora.gguf' dosyasını Ollama'da Modelfile ile Qwen 2.5 3B üzerine giydirerek çalıştırabilirsiniz.")