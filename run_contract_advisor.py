import os
import sys
import torch
from unsloth import FastLanguageModel

# Terminal çıktı karakter kodlaması (Windows desteği)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def load_advisor_model():
    lora_path = "Finetuned_model/hukuk_model_lora"
    if not os.path.exists(lora_path):
        lora_path = "output/hukuk_model_lora"
    if not os.path.exists(lora_path):
        print(f"[HATA] Model klasörü bulunamadı!")
        print("Lütfen 'Finetuned_model/hukuk_model_lora' klasörünün varlığından emin olun.")
        sys.exit(1)
        
    print(f"[İLGİ] Yapay Zeka Hukuk Danışmanı Yükleniyor ({lora_path})...")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = lora_path,
        max_seq_length = 2048,
        dtype = None,
        load_in_4bit = True,
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer

def analyze_clause(model, tokenizer, clause_text):
    system_prompt = "Sen uzman bir sözleşme danışmanısın. Verilen sözleşme maddesini hukuki olarak analiz et ve Geçerli/Geçersiz olduğuna karar ver."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Sözleşme Maddesi: {clause_text}"}
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=350,
        use_cache=True,
        temperature=0.2,
    )
    
    input_len = inputs["input_ids"].shape[1]
    response = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
    return response

def main():
    print("=" * 75)
    print("      YAPAY ZEKA TÜRK HUKUKU SÖZLEŞME DANIŞMANI (FINE-TUNED MODEL)")
    print("=" * 75)
    
    model, tokenizer = load_advisor_model()
    print("\n[BAŞARILI] Model hazır! Analiz etmek istediğiniz sözleşme maddesini yazın.\n")
    
    sample_clauses = [
        "İşçinin kıdem tazminatı tavan sınırlaması uygulanmaksızın brüt ücretinin 4 katı olarak ödenir.",
        "Deneme süresi 6 ay olarak belirlenmiştir.",
        "İşçi sözleşmeyi haklı nedenle feshetse dahi cezai şart ödemeyi kabul eder."
    ]
    
    print("Örnek maddelerden birini test etmek için 1, 2 veya 3 yazabilir ya da kendi maddenizi yazabilirsiniz.")
    print("Çıkış yapmak için 'q' yazın.\n")
    
    while True:
        try:
            user_input = input("\nSözleşme Maddesi Girin: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['q', 'quit', 'exit', 'cikis']:
                print("\nProgram kapatılıyor. İyi çalışmalar!")
                break
                
            if user_input in ['1', '2', '3']:
                idx = int(user_input) - 1
                user_input = sample_clauses[idx]
                print(f"[Örnek Seçildi]: {user_input}")
                
            print("\n[ANALİZ EDİLİYOR] Hukuki dayanaklar ve emredici kurallar kontrol ediliyor...\n")
            analysis = analyze_clause(model, tokenizer, user_input)
            
            print("-" * 75)
            print("ANALİZ VE KARAR:")
            print(analysis)
            print("-" * 75)
            
        except KeyboardInterrupt:
            print("\nÇıkış yapıldı.")
            break
        except Exception as e:
            print(f"[HATA] İnceleme sırasında hata oluştu: {e}")

if __name__ == "__main__":
    main()
