import os
import re
import sys
import io


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import easyocr
except ImportError:
    print("EasyOCR kütüphanesi bulunamadı!")
    print("Çalıştırmak için terminalde şu komutu çalıştırın:")
    print("pip install easyocr")
    exit()

def test_ocr_and_chunking(image_path):
    print(f"\n[BİLGİ] '{image_path}' dosyası OCR ile okunuyor...")
    print("[BİLGİ] Bu işlem bilgisayarınızın hızına göre birkaç saniye sürebilir...\n")
    
    # İlk çalıştırıldığında dil modellerini indireceği için biraz bekletebilir.
    reader = easyocr.Reader(['tr', 'en'])
    
    # detail=0 sadece metni verir, detail=1 olsaydı koordinatları (bounding box) da verirdi.
    result = reader.readtext(image_path, detail=0)
    
    # Bulunan tüm metin parçalarını alt alta birleştiriyoruz
    full_text = "\n".join(result)
    
    
    print("="*50)
    print("2. AŞAMA: YAPISAL PARÇALAMA (STRUCTURAL CHUNKING) SİMÜLASYONU")
    print("="*50)
    

    
    pattern = r'(?i)(?:\n|^)\s*(Madde\s*\d+\.?|\d+\.\s*[A-ZĞÜŞİÖÇ])'
    
    chunks = re.split(pattern, full_text)
    
    if len(chunks) > 1:
        print("[BİLGİ] Sözleşme maddeleri başarıyla ayrıştırıldı!\n")
        
        if chunks[0].strip():
            print("> BÖLÜM: [Önsöz / Başlangıç]")
            print(f"  İÇERİK: {chunks[0].strip()[:100]}...\n")
            
        for i in range(1, len(chunks), 2):
            madde_basligi = chunks[i].strip()
            madde_icerigi = chunks[i+1].strip()
            print(f"> BÖLÜM: [{madde_basligi}]")
            print(f"  İÇERİK: {madde_icerigi[:150]}...\n")
            print("-" * 30)
    else:
        print("[UYARI] Spesifik bir 'Madde' başlığı bulunamadı.")
        print("Metin tek parça (chunk) olarak değerlendirildi.")

if __name__ == "__main__":
    test_image_name = "belirsiz-sureli-is-sozlesmesi-1.png"
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, test_image_name)
    
    if os.path.exists(image_path):
        test_ocr_and_chunking(image_path)
    else:
        print(f"[HATA] Dosya bulunamadı: {image_path}")
        print("Lütfen scripti resim dosyalarıyla aynı klasörde çalıştırdığınızdan emin olun.")
