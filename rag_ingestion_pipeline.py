import os
import sys
import io
import easyocr
from image_preprocessing import preprocess_for_ocr
from legal_chunker import parse_legal_text, flatten_chunks

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_pipeline(image_filename):
    # OCR (Okuma) ve Chunking (Hukuki Metin Parçalama) işlemlerini tek bir uçtan uca akışta çalıştırıp txt olarak dışarı aktarır.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, image_filename)
    
    if not os.path.exists(image_path):
        return

    processed_image = preprocess_for_ocr(image_path, save_debug=False)
    
    reader = easyocr.Reader(['tr'])
    ocr_result = reader.readtext(processed_image, detail=0)
    full_text = "\n".join(ocr_result)
    
    raw_txt_path = os.path.join(current_dir, "ocr_ham_metin.txt")
    with open(raw_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    root_node = parse_legal_text(full_text)
    rag_chunks = flatten_chunks(root_node)
    
    parsed_txt_path = os.path.join(current_dir, "ocr_parcalanmis_metin.txt")
    with open(parsed_txt_path, "w", encoding="utf-8") as f:
        for idx, chunk in enumerate(rag_chunks, 1):
            f.write(f"CHUNK #{idx}\n")
            f.write(f"BAĞLAM (METADATA) : {chunk['metadata']['hierarchy']}\n")
            f.write(f"SEVİYE (LEVEL)    : {chunk['metadata']['level']}\n")
            f.write(f"METİN             : {chunk['text']}\n")
            f.write("-" * 60 + "\n")
            
if __name__ == "__main__":
    run_pipeline("belirsiz-sureli-is-sozlesmesi-1.png")
