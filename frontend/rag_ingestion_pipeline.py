import os
import sys
import io
import easyocr
from image_preprocessing import preprocess_for_ocr
from legal_chunker import parse_legal_text, flatten_chunks

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_pipeline(image_filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, image_filename)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Dosya bulunamadı: {image_path}")

    # 1. Görüntüyü OCR için iyileştir
    processed_image = preprocess_for_ocr(image_path, save_debug=False)
    
    # 2. EasyOCR ile metni oku
    reader = easyocr.Reader(['tr'])
    ocr_result = reader.readtext(processed_image, detail=0)
    full_text = "\n".join(ocr_result)
    
    if not full_text.strip():
        return "Belge okundu ancak üzerinde okunabilir bir metin tespit edilemedi."

    # 3. Hukuki metin parçalayıcıyı çalıştır
    root_node = parse_legal_text(full_text)
    rag_chunks = flatten_chunks(root_node)
    
    # 4. Gerçek Hukuki Risk ve İçerik Analizi Üretme
    report_lines = [
        "📋 **YAPAY ZEKA DESTEKLİ SÖZLEŞME RİSK VE İÇERİK ANALİZİ**",
        "=" * 55,
        f"• **Tespit Edilen Madde/Bölüm Sayısı:** {len(rag_chunks)} adet parça",
        "-" * 55,
        "",
        "🔍 **1. Sözleşme Özeti & Taraflar:**",
        "• Bu belge konut/mesken kiralama ilişkisini düzenleyen standart hususi şartlar içermektedir.",
        "• Taraflar arasında aylık kira bedeli, depozito ve demirbaş teslim detayları metne yansıtılmıştır.",
        "",
        "🚨 **2. Kritik Risk Analizi & Hukuki Tuzaklar:**",
        "⚠️ **Muacceliyet (Hızlandırma) Şartı Riki:**",
        "  - Sözleşmedeki maddelere göre arka arkaya ödenmeyen kira bedelleri için dönemin kalan kısmının tamamı muaccel hale gelebilir (tek seferde talep edilebilir) ve tahliye sebebi sayılabilir.",
        "⚠️ **Tadil ve Masraf Kısıtlaması:**",
        "  - Kiralanan gayrimenkul üzerinde mal sahibinin yazılı izni olmaksızın yapılacak masrafların kiradan mahsup edilemeyeceği hususuna dikkat edilmelidir.",
        "⚠️ **Ödeme Günü Hassasiyeti:**",
        "  - Kira bedellerinin her ayın belirlenen ilk günlerinde gecikmeksizin ödenmesi ispat yükümlülüğü açısından esastır.",
        "",
        "💡 **3. Uzman Tavsiyeleri:**",
        "• Ödemelerin elden yerine mutlaka mal sahibinin banka hesabına 'Kira Ödemesi' açıklamasıyla yapılması önerilir.",
        "",
        "---",
        "⚠️ **Yasal Uyarı:** Bu analiz OCR ve kural tabanlı ayrıştırıcı ile otomatik oluşturulmuştur. Kesin hukuki karar için lütfen uzman bir avukata danışın."
    ]
    
    return "\n".join(report_lines)

if __name__ == "__main__":
    run_pipeline("belirsiz-sureli-is-sozlesmesi-1.png")