# OCR Test Raporu

## Amaç

Türkçe kira sözleşmeleri üzerinde Unlimited-OCR modelinin performansını değerlendirmek.

## Kullanılan Model

- Model: Unlimited-OCR (Baidu)
- Platform: Hugging Face

<img width="1440" height="730" alt="OCRoutput2jpg" src="https://github.com/user-attachments/assets/3509d0e4-e19b-4716-b533-55cfe7866c38" />

<img width="1440" height="751" alt="OCRoutput1" src="https://github.com/user-attachments/assets/1b8e2674-1b0d-4a63-bf89-af48a54aeeac" />

## Test Edilen Dosyalar

| Dosya | Sonuç |
|-------|-------|
| KiraSözleşmesi.pdf | ✅ Başarılı |
| KiraSözleşmesiJPG.jpg | ✅ Başarılı |

## Gözlemler

- Türkçe karakterler (ç, ğ, ı, İ, ö, ş, ü) doğru şekilde okundu.
- "Madde 1", "Madde 2" gibi madde numaraları korundu.
- Metin düzeni büyük ölçüde korundu.
- Belirgin bir OCR hatası gözlemlenmedi.

## Sonuç

Unlimited-OCR modeli, Türkçe sözleşmeler üzerinde başarılı sonuç vermiştir. Projenin OCR aşamasında kullanılmaya uygundur.

İlk testler doğrultusunda Unlimited-OCR modeli proje için uygun bulunmuştur. Bir sonraki sprintte daha karmaşık görüntüler üzerinde doğruluk analizi yapılarak modelin performansı detaylı şekilde değerlendirilecektir.
