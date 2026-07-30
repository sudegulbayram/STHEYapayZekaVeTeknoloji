import os
import json

try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError:
    print("Gerekli kütüphaneler bulunamadı! Çalıştırmak için şu komutu girin:")
    print("pip install openai python-dotenv")
    exit()

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
    print("[HATA] Lütfen .env dosyasını açıp 'your_deepseek_api_key_here' kısmına geçerli bir API anahtarı yapıştırın.")
    exit()

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def generate_synthetic_contract_data():
    print("[BİLGİ] DeepSeek API'sine bağlanılıyor...")
    print("[BİLGİ] SLM eğitimi için Sentetik CoT (Chain of Thought) verisi üretiliyor...\n")
    
    system_prompt = """
    Sen uzman bir Türk Hukukçusu ve Sözleşme Analistisin. 
    Görevin, sana verilen bir sözleşme türü için kasıtlı olarak "riskli" bir madde üretmek, 
    ardından bu maddenin NEDEN riskli olduğunu adım adım hukuki gerekçelerle (Chain of Thought - CoT) açıklamaktır.
    
    Lütfen çıktını MÜTLAKA aşağıdaki JSON formatında ver:
    {
      "contract_type": "Sözleşme Türü",
      "clause_text": "Riskli maddenin tam metni",
      "is_risky": true,
      "chain_of_thought": [
         "Adım 1: Maddenin içerdiği yükümlülüğün analizi...",
         "Adım 2: Hukuki niyetin (intent) değerlendirilmesi...",
         "Adım 3: Kanunlara, Yargıtay kararlarına veya genel teamüllere aykırılık tespiti..."
      ],
      "risk_summary": "Kısa ve net risk özeti",
      "correction_suggestion": "Bu maddenin risksiz, her iki taraf için dengeli ve ideal hali"
    }
    """

    user_prompt = "Lütfen 'Gizlilik Sözleşmesi (NDA)' için süre sınırı olmayan, sadece tek tarafı bağlayan ve astronomik bir cezai şart içeren son derece riskli bir madde yaz ve adım adım analiz et."

    try:

        response = client.chat.completions.create(
            model="deepseek-v4-flash", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        message = response.choices[0].message
        
        result = message.content
        parsed_result = json.loads(result)
        
        print("="*60)
        print("  DEEPSEEK ÇIKTISI (SLM EĞİTİM VERİSİ - CoT FORMATI)")
        print("="*60)
        
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            print("[NATIVE THINKING MODE (Modelin Kendi Düşüncesi)]:")
            print(message.reasoning_content)
            print("-" * 60)
            
        print(json.dumps(parsed_result, indent=4, ensure_ascii=False))
        print("="*60)
        print("\n[BAŞARILI] Bu kalitedeki verilerden 5-10 bin tane üretip kendi Llama-3 modelimizi eğiteceğiz!")
        
    except Exception as e:
        print(f"[HATA] API Çağrısı sırasında bir sorun oluştu:\n{e}")

if __name__ == "__main__":
    generate_synthetic_contract_data()
