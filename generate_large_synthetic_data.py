import os
import json
import random
import time
from datetime import datetime

try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError:
    print("Gerekli kütüphaneler bulunamadı! Lütfen çalıştırın: 'pip install openai python-dotenv'")
    exit()

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    print("[HATA] .env dosyasında DEEPSEEK_API_KEY bulunamadı.")
    exit()

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Hedef sentetik veri sayısı (2000 - 3000 arası, varsayılan 2500)
TARGET_TOTAL_SAMPLES = 2500
OUTPUT_FILE = "fine_tuning_dataset_large.jsonl"
TXT_RULES_FILE = "Yapay Zeka Sözleşme Danışmanı İçin Fine-Tuning ve RAG Veri Seti Planlaması.txt"

# Çeşitliliği artırmak için genişletilmiş parametreler
SECTORS = [
    "İnşaat", "Yazılım & Teknoloji", "Tekstil", "Gıda & İçecek", "Otomotiv", 
    "Lojistik & Taşımacılık", "Sağlık & İlaç", "E-Ticaret", "Bankacılık & Finans", 
    "Turizm & Otelcilik", "Enerji & Madencilik", "Perakende & Mağazacılık", "Medya & Reklam"
]
CURRENCIES = ["TL", "Türk Lirası", "USD", "EUR"]
TONES = [
    "Resmi ve sert bir hukuki dil", 
    "Daha modern, sade ve anlaşılır bir sözleşme dili", 
    "Aşırı karmaşık ve eski Türkçe hukuki terimlerin (butlan, fesih, muacceliyet vb.) ağırlıkta olduğu dil",
    "Uluslararası kurumsal şirket şablonu dili"
]

COMPANY_PREFIXES = ["ABC", "XYZ", "Beta", "Alfa", "Kuzey", "Güney", "Anadolu", "Global", "Vortex", "Bosphorus", "Tekno", "Mega", "Zirve"]
COMPANY_SUFFIXES = ["A.Ş.", "Ltd. Şti.", "Holding", "Yatırım A.Ş.", "Teknoloji Ltd.", "Yapı A.Ş."]

SYSTEM_PROMPT = """Sen uzman bir Türk Hukuku akademisyeni ve avukatısın. 
Amacın, yapay zeka modelini eğitmek (fine-tuning) için yüksek kaliteli sentetik sözleşme verisi üretmektir.

DİKKAT ETMEN GEREKEN ÇOK ÖNEMLİ KURALLAR (HALÜSİNASYONU ÖNLEMEK İÇİN):
1. Asla sana verilen Yasal Dayanak ve İhlal Mantığı dışına çıkma. Kural neyse sadece onu uygula.
2. Ürettiğin maddeler tamamen farklı senaryolara, farklı şirket tiplerine (A.Ş., Ltd. Şti.) ve sektörlere ait olmalı. Hep aynı taraf isimlerini kullanma, senaryoyu çeşitlendir.
3. Her madde için adım adım CoT (Chain of Thought) gerekçelendirme yazacaksın.

SADECE AŞAĞIDAKİ JSON FORMATINDA ÇIKTI VER:
{
  "synthetic_data": [
    {
      "type": "invalid",
      "clause": "Üretilen geçersiz (hatalı/kanuna aykırı) sözleşme maddesi metni...",
      "reasoning": "Adım adım düşünce süreci: 1. Sözleşme incelendi. 2. İlgili kanun (TBK/İK vb.) dikkate alındı. 3. Şu sebepten dolayı hukuka aykırıdır. 4. Geçersizdir.",
      "label": "Geçersiz"
    },
    {
      "type": "valid",
      "clause": "Üretilen geçerli (kanuna uygun) sözleşme maddesi metni...",
      "reasoning": "Adım adım düşünce süreci: 1. Sözleşme incelendi. 2. İlgili kural ihlal edilmemiştir. 3. Şu yüzden hukuka uygundur. 4. Geçerlidir.",
      "label": "Geçerli"
    }
  ]
}
"""

def generate_random_company_name():
    prefix = random.choice(COMPANY_PREFIXES)
    suffix = random.choice(COMPANY_SUFFIXES)
    sector = random.choice(["Yazılım", "İnşaat", "Lojistik", "Gıda", "Danışmanlık", "Tekstil", "Enerji"])
    return f"{prefix} {sector} {suffix}"

def generate_dataset_for_rule(rule_data, attempt=1):
    sector = random.choice(SECTORS)
    currency = random.choice(CURRENCIES)
    tone = random.choice(TONES)
    comp1 = generate_random_company_name()
    comp2 = generate_random_company_name()
    
    user_prompt = f"""
    Aşağıdaki kurala göre 2 geçerli, 2 geçersiz sözleşme maddesi ve CoT analizi üret.
    
    Kural Konusu: {rule_data['konu']}
    Yasal Dayanak: {rule_data['dayanak']}
    Örnek İhlal: {rule_data['ihlal_ornegi']}
    Modelin Yapması Gereken Analiz: {rule_data['analiz_mantigi']}
    
    ZORUNLU SENARYO (Çeşitlilik İçin):
    - Sektör: {sector}
    - Kullanılacak Para Birimi: {currency}
    - Yazım Tonu: {tone}
    - Taraf Şirketler: {comp1} ve {comp2}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        
        result_json = json.loads(response.choices[0].message.content)
        return result_json.get("synthetic_data", [])
        
    except Exception as e:
        print(f"[HATA] API çağrısında hata (Deneme {attempt}/3): {e}")
        if attempt < 3:
            time.sleep(4)
            return generate_dataset_for_rule(rule_data, attempt + 1)
        return []

def parse_rules_from_txt(filepath):
    rules = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            
        i = 0
        while i < len(lines):
            if lines[i].isdigit() and i + 5 < len(lines):
                rule = {
                    "no": lines[i],
                    "konu": lines[i+1],
                    "dayanak": lines[i+2],
                    "emredicilik": lines[i+3],
                    "ihlal_ornegi": lines[i+4],
                    "analiz_mantigi": lines[i+5]
                }
                rules.append(rule)
                i += 6
            else:
                i += 1
    except Exception as e:
        print(f"[HATA] Dosya okuma hatası: {e}")
        
    return rules

def count_existing_samples(filepath):
    if not os.path.exists(filepath):
        return 0
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count

def main():
    print("=" * 70)
    print(f"  BÜYÜK SENTETİK VERİ ÜRETİM SCRIPT'İ (Hedef: {TARGET_TOTAL_SAMPLES} Veri)")
    print("=" * 70)
    
    rules = parse_rules_from_txt(TXT_RULES_FILE)
    
    if not rules:
        print(f"[UYARI] '{TXT_RULES_FILE}' dosyasından kural okunamadı.")
        return
        
    print(f"[BİLGİ] {len(rules)} adet hukuki kural yüklendi.")
    
    current_count = count_existing_samples(OUTPUT_FILE)
    if current_count > 0:
        print(f"[BİLGİ] '{OUTPUT_FILE}' dosyasında zaten {current_count} adet veri bulundu. Üretime kalınan yerden devam edilecek.")
    else:
        print(f"[BİLGİ] Yeni dosya oluşturuluyor: '{OUTPUT_FILE}'")

    start_time = time.time()
    pass_number = (current_count // (len(rules) * 4)) + 1

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        while current_count < TARGET_TOTAL_SAMPLES:
            print(f"\n--- [TUR {pass_number}] Bütün kurallar üzerinden geçiliyor... ---")
            
            # Kuralları karıştırarak döngüye sok (çeşitlilik için)
            rule_order = list(rules)
            random.shuffle(rule_order)
            
            for idx, rule in enumerate(rule_order, 1):
                if current_count >= TARGET_TOTAL_SAMPLES:
                    break

                print(f"[{current_count}/{TARGET_TOTAL_SAMPLES}] (%{int(current_count/TARGET_TOTAL_SAMPLES*100)}) Kural #{rule['no']}: {rule['konu'][:40]}...", end="", flush=True)
                
                generated_data = generate_dataset_for_rule(rule)
                added = 0
                
                if generated_data:
                    for data in generated_data:
                        if current_count >= TARGET_TOTAL_SAMPLES:
                            break
                        
                        ft_line = {
                            "messages": [
                                {"role": "system", "content": "Sen uzman bir sözleşme danışmanısın. Verilen sözleşme maddesini hukuki olarak analiz et ve Geçerli/Geçersiz olduğuna karar ver."},
                                {"role": "user", "content": f"Sözleşme Maddesi: {data['clause']}"},
                                {"role": "assistant", "content": f"<thought>\n{data['reasoning']}\n</thought>\n\nSonuç: {data['label']}"}
                            ]
                        }
                        f.write(json.dumps(ft_line, ensure_ascii=False) + "\n")
                        f.flush()
                        current_count += 1
                        added += 1

                print(f" -> {added} veri eklendi.")
                time.sleep(1.2) # API Rate-Limit koruması
                
            pass_number += 1

    elapsed_minutes = (time.time() - start_time) / 60
    print("\n" + "=" * 70)
    print(f"[BAŞARILI] Toplam {current_count} adet veri '{OUTPUT_FILE}' dosyasına kaydedildi!")
    print(f"Toplam Geçen Süre: {elapsed_minutes:.1f} dakika.")
    print("=" * 70)

if __name__ == "__main__":
    main()
