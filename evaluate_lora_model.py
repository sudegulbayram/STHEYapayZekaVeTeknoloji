import sys
import torch
from unsloth import FastLanguageModel

# Windows terminal çıktı uyumluluğu
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

base_model_path = "./unsloth"
lora_model_path = "output/hukuk_model_lora"

print("=" * 70)
print("  EĞİTİLMİŞ LORA MODELİ PERFORMANS VE HALÜSİNASYON TESTİ")
print("=" * 70)

print(f"\n[1/3] Model ve Tokenizer yükleniyor: {lora_model_path}...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = lora_model_path,
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)

FastLanguageModel.for_inference(model) # 2 kat hızlı çıkarım (inference) modu

system_prompt = "Sen uzman bir sözleşme danışmanısın. Verilen sözleşme maddesini hukuki olarak analiz et ve Geçerli/Geçersiz olduğuna karar ver."

# Test Senaryoları (5 Geçersiz, 5 Geçerli Hukuki Maddeler)
TEST_CASES = [
    {
        "id": 1,
        "expected": "Geçersiz",
        "topic": "Kıdem Tazminatı Tavanı İhlali",
        "clause": "İşçinin kıdem tazminatı, herhangi bir yasal tavan sınırlaması dikkate alınmaksızın son aldığı brüt ücretin 3 katı üzerinden hesaplanarak ödenir."
    },
    {
        "id": 2,
        "expected": "Geçersiz",
        "topic": "Deneme Süresi Üst Sınır İhlali",
        "clause": "Taraflar işbu sözleşme kapsamında işçinin deneme süresini 6 ay olarak kararlaştırmışlardır."
    },
    {
        "id": 3,
        "expected": "Geçersiz",
        "topic": "Tek Taraflı Cezai Şart Yasağı (TBK 420)",
        "clause": "İşçi sözleşmeyi haklı bir neden olmaksızın süresinden önce feshederse 50.000 TL cezai şart öder. İşverenin feshinde ise herhangi bir ceza ödenmez."
    },
    {
        "id": 4,
        "expected": "Geçersiz",
        "topic": "Kira Sözleşmesinde Muacceliyet Kaydı Yasağı (TBK 346)",
        "clause": "Kiracı, kira bedelini üst üste iki ay ödemezse, kira sözleşmesinin sonuna kadar olan tüm gelecek ayların kira bedelleri muaccel hale gelir ve derhal tahsil edilir."
    },
    {
        "id": 5,
        "expected": "Geçersiz",
        "topic": "Yıllık İzin Hakkından Feragat Yasağı",
        "clause": "İşçi, şirketin yoğun çalışma dönemlerinde kullanamadığı yıllık ücretli izin haklarından peşinen ve gayrikabili rücu olarak feragat ettiğini kabul eder."
    },
    {
        "id": 6,
        "expected": "Geçerli",
        "topic": "Kanuna Uygun Fazla Çalışma Maddesi",
        "clause": "İşçinin haftalık 45 saati aşan fazla çalışmaları için saatlik ücreti, normal çalışma saatlik ücretinin %50 zamlı miktarı üzerinden hesaplanarak ödenir."
    },
    {
        "id": 7,
        "expected": "Geçerli",
        "topic": "Kanuna Uygun Makul Rekabet Yasağı",
        "clause": "İşçi, sözleşmenin sona ermesinden itibaren 1 yıl süreyle ve sadece İstanbul ili sınırları içerisinde işverenle aynı konuda faaliyet gösteren rakip firmalarda çalışmamayı taahhüt eder."
    },
    {
        "id": 8,
        "expected": "Geçerli",
        "topic": "Kanuna Uygun Yıllık Ücretli İzin Maddesi",
        "clause": "İşçiye verilecek yıllık ücretli izin süreleri, İş Kanunu'nda kıdem süresine göre belirlenen asgari yasal izin sürelerinden az olmamak üzere uygulanacaktır."
    },
    {
        "id": 9,
        "expected": "Geçerli",
        "topic": "Kanuna Uygun Kira Ödeme Maddesi",
        "clause": "Kiracı, aylık kira bedeli olan 25.000 TL'yi her ayın 5. günü akşamına kadar kiralayanın belirteceği banka hesabına havale/EFT yoluyla ödeyecektir."
    },
    {
        "id": 10,
        "expected": "Geçerli",
        "topic": "Kanuna Uygun Gizlilik Sözleşmesi Maddesi",
        "clause": "Taraflar, işbu sözleşme kapsamında öğrendikleri ticari sırları ve müşteri bilgilerini sözleşme süresince ve sözleşmenin sona ermesinden itibaren 2 yıl boyunca 3. kişilerle paylaşmamayı taahhüt eder."
    }
]

correct_count = 0
total_count = len(TEST_CASES)

print("\n[2/3] Testler Başlatılıyor (10 Farklı Hukuki Senaryo)...\n")

for test in TEST_CASES:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Sözleşme Maddesi: {test['clause']}"}
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        use_cache=True,
        temperature=0.2, # Düşük sıcaklık = Minimized Hallucination
    )
    
    input_len = inputs["input_ids"].shape[1]
    response = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
    
    # Karar tespiti (Sonuç: Geçerli / Geçersiz)
    predicted = "Bilinmiyor"
    if "Sonuç: Geçersiz" in response or "Geçersizdir" in response or "geçersiz" in response.lower():
        predicted = "Geçersiz"
    elif "Sonuç: Geçerli" in response or "Geçerlidir" in response or "geçerli" in response.lower():
        predicted = "Geçerli"
        
    is_correct = (predicted == test['expected'])
    if is_correct:
        correct_count += 1
        status_str = "PASSED [DOĞRU]"
    else:
        status_str = "FAILED [YANLIŞ]"

    print("-" * 75)
    print(f"Test #{test['id']} | Konu: {test['topic']}")
    print(f"Sözleşme Maddesi: {test['clause']}")
    print(f"Beklenen: {test['expected']} | Model Tahmini: {predicted} -> {status_str}")
    print(f"\n[Modelin Akıl Yürütmesi (CoT Chain of Thought)]:\n{response}")

print("\n" + "=" * 70)
print(f"[3/3] TEST SONUÇLARI ÖZETİ")
print(f"Toplam Test: {total_count}")
print(f"Doğru Tahmin: {correct_count}")
print(f"Yanlış Tahmin / Halüsinasyon: {total_count - correct_count}")
print(f"Doğruluk Oranı (Accuracy): %{(correct_count / total_count) * 100:.1f}")
print("=" * 70)
