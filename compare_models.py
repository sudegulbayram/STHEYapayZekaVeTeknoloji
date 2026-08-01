import os
import sys
import torch
from unsloth import FastLanguageModel

# Output file path (Bunu output/ klasörüne yazıyoruz ki Windows üzerinde kolayca açılabilsin)
TXT_OUTPUT_FILE = "output/model_comparison_results.txt"

sys.stdout.reconfigure(encoding='utf-8')

system_prompt = "Sen uzman bir sözleşme danışmanısın. Verilen sözleşme maddesini hukuki olarak analiz et ve Geçerli/Geçersiz olduğuna karar ver."

# Test Senaryoları (Birebir Aynı 10 Hukuki Senaryo)
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

def evaluate_model(lora_path, model_label):
    print(f"\n[{model_label}] Model Yükleniyor: {lora_path}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = lora_path,
        max_seq_length = 2048,
        dtype = None,
        load_in_4bit = True,
    )
    FastLanguageModel.for_inference(model)

    results = []
    correct_count = 0

    for test in TEST_CASES:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Sözleşme Maddesi: {test['clause']}"}
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            use_cache=True,
            temperature=0.2,
        )
        
        input_len = inputs["input_ids"].shape[1]
        response = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
        
        predicted = "Bilinmiyor"
        if "Sonuç: Geçersiz" in response or "Geçersizdir" in response or "geçersiz" in response.lower():
            predicted = "Geçersiz"
        elif "Sonuç: Geçerli" in response or "Geçerlidir" in response or "geçerli" in response.lower():
            predicted = "Geçerli"

        is_correct = (predicted == test['expected'])
        if is_correct:
            correct_count += 1
            
        results.append({
            "test": test,
            "predicted": predicted,
            "is_correct": is_correct,
            "response": response
        })

    # Belleği temizleyelim
    del model
    del tokenizer
    torch.cuda.empty_cache()

    return results, correct_count

def main():
    print("=" * 80)
    print("  MODEL KARŞILAŞTIRMA TESTİ (2500 Verili Model vs 200 Verili Model)")
    print("=" * 80)

    # 1. MODEL: 2500 Veri ile Eğitilmiş Model (output/hukuk_model_lora)
    model1_path = "output/hukuk_model_lora"
    model1_name = "BÜYÜK MODEL (2500 Veri Seti - output)"
    results1, correct1 = evaluate_model(model1_path, model1_name)

    # 2. MODEL: 200 Veri ile Eğitilmiş Model (outputwithsmallfinetune/hukuk_model_lora)
    model2_path = "outputwithsmallfinetune/hukuk_model_lora"
    model2_name = "KÜÇÜK MODEL (200 Veri Seti - outputwithsmallfinetune)"
    results2, correct2 = evaluate_model(model2_path, model2_name)

    # TXT Raporunu Hazırlayalım
    report_lines = []
    report_lines.append("=" * 85)
    report_lines.append("        HUKUKİ SÖZLEŞME ANALİZİ - MODEL PERFORMANS KARŞILAŞTIRMA RAPORU")
    report_lines.append("=" * 85)
    report_lines.append(f"Model 1: {model1_name}")
    report_lines.append(f"Model 2: {model2_name}")
    report_lines.append(f"Toplam Test Sayısı: {len(TEST_CASES)}")
    report_lines.append("-" * 85)
    report_lines.append(f"Model 1 (2500 Veri) Doğruluk Oranı: %{(correct1/len(TEST_CASES))*100:.1f} ({correct1}/{len(TEST_CASES)} Doğru)")
    report_lines.append(f"Model 2 (200 Veri)  Doğruluk Oranı: %{(correct2/len(TEST_CASES))*100:.1f} ({correct2}/{len(TEST_CASES)} Doğru)")
    report_lines.append("=" * 85 + "\n\n")

    report_lines.append("" + "=" * 85)
    report_lines.append("                       DETAYLI SENARYO KARŞILAŞTIRMALARI")
    report_lines.append("=" * 85 + "\n")

    for i in range(len(TEST_CASES)):
        r1 = results1[i]
        r2 = results2[i]
        test = TEST_CASES[i]

        report_lines.append(f"-------------------------------------------------------------------------------------")
        report_lines.append(f"TEST #{test['id']} | Konu: {test['topic']}")
        report_lines.append(f"SÖZLEŞME MADDESİ: \"{test['clause']}\"")
        report_lines.append(f"BEKLENEN DOĞRU CEVAP: {test['expected']}\n")

        status1_str = "DOĞRU [PASSED]" if r1['is_correct'] else "YANLIŞ / HALÜSİNASYON [FAILED]"
        report_lines.append(f"--- [MODEL 1: 2500 VERİ] ---")
        report_lines.append(f"Tahmin: {r1['predicted']} -> {status1_str}")
        report_lines.append(f"Akıl Yürütme (CoT):\n{r1['response']}\n")

        status2_str = "DOĞRU [PASSED]" if r2['is_correct'] else "YANLIŞ / HALÜSİNASYON [FAILED]"
        report_lines.append(f"--- [MODEL 2: 200 VERİ] ---")
        report_lines.append(f"Tahmin: {r2['predicted']} -> {status2_str}")
        report_lines.append(f"Akıl Yürütme (CoT):\n{r2['response']}\n")

    report_content = "\n".join(report_lines)

    # TXT Dosyasına Yazalım
    with open(TXT_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)

    print("\n" + "=" * 80)
    print(f"[BAŞARILI] Karşılaştırma tamamlandı!")
    print(f"Büyük Model (2500 Veri): %{(correct1/len(TEST_CASES))*100:.1f} Başarı ({correct1}/{len(TEST_CASES)})")
    print(f"Küçük Model (200 Veri):  %{(correct2/len(TEST_CASES))*100:.1f} Başarı ({correct2}/{len(TEST_CASES)})")
    print(f"Detaylı rapor TXT olarak '{TXT_OUTPUT_FILE}' konumuna yazıldı.")
    print("=" * 80)

if __name__ == "__main__":
    main()
