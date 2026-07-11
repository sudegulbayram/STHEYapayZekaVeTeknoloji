import re

CLAUSE_KEYWORDS = {
    # Kira sözleşmeleri
    "depozito": "depozito",
    "kira bedeli": "kira_bedeli",
    "kira artış": "kira_artis",
    "tahliye": "tahliye",
    "kiralanan": "kiralanan",
    
    # Ödeme
    "ücret": "ucret",
    "ödeme": "odeme",
    "fatura": "fatura",
    "gecikme faizi": "gecikme_faizi",
    "avans": "avans",
    
    # Fesih ve sona erme
    "fesih": "fesih",
    "sona erme": "sona_erme",
    "süre": "sure",
    "yenileme": "yenileme",
    "uzatma": "uzatma",
    
    # Ceza ve tazminat
    "cezai şart": "cezai_sart",
    "tazminat": "tazminat",
    "zarar": "zarar",
    "hasar": "hasar",
    
    # Gizlilik ve fikri mülkiyet
    "gizlilik": "gizlilik",
    "gizli bilgi": "gizli_bilgi",
    "fikri mülkiyet": "fikri_mulkiyet",
    "telif": "telif",
    
    # Sorumluluk
    "sorumluluk": "sorumluluk",
    "yükümlülük": "yukumluluk",
    "garanti": "garanti",
    "taahhüt": "taahhut",
    
    # Sigorta
    "sigorta": "sigorta",
    
    # Devir ve temlik
    "devir": "devir",
    "temlik": "temlik",
    "alt kiracı": "alt_kiraci",
    
    # Uyuşmazlık
    "uyuşmazlık": "uyusmazlik",
    "tahkim": "tahkim",
    "mahkeme": "mahkeme",
    "yargı": "yargi",
    
    # Değişiklik
    "değişiklik": "degisiklik",
    "tadilat": "tadilat",
    
    # İş sözleşmeleri
    "deneme süresi": "deneme_suresi",
    "kıdem": "kidem",
    "ihbar": "ihbar",
    "fazla mesai": "fazla_mesai",
    "görev tanımı": "gorev_tanimi",

    "ibra": "ibra",
    "ibraname": "ibra",
    "zincirleme": "zincirleme_sozlesme",
    "belirli süreli": "belirli_sureli",
    "muacceliyet": "muacceliyet",
    "ara dinlenme": "ara_dinlenme",
    "fazla çalışma": "fazla_calisma",
    "gece çalışması": "gece_calismasi",
    "haftalık çalışma": "haftalik_calisma",
    "asgari ücret": "asgari_ucret",
    "doğum izni": "dogum_izni",
    "yıllık izin": "yillik_izin",
    "işe iade": "ise_iade",
    "rekabet yasağı": "rekabet_yasagi",
    "zamanaşımı": "zamanasimi",
    "kefil": "kefil",
    "bağlantılı sözleşme": "baglantili_sozlesme",
    "takas": "takas",
    "arabuluculuk": "arabuluculuk",
    "ayıplı": "ayipli_teslim",
    "otomatik uzama": "otomatik_uzama",
    "esaslı bakım": "esasli_bakim",
    "erken tahliye": "erken_tahliye",
    "temerrüt": "temerrut",
}

class ChunkNode:
    # Hiyerarşik ağaç düğümü. level=0 sözleşme, level=1 bölüm, level=2 madde ifade eder.
    def __init__(self, title, level, content=""):
        self.title = title
        self.level = level
        self.content = content
        self.children = []

    def to_dict(self):
        # Ağaç yapısını JSON'a dönüştürür
        return {
            "title": self.title,
            "level": self.level,
            "content": self.content.strip(),
            "children": [child.to_dict() for child in self.children]
        }
    

def detect_clause_type(text):
    #Sık kullanılan anahtar kelimelere göre metin parçasının hangi hukuki başlığa ait olduğunu belirler.
    text_lower = text.lower()
    found = [clause_type for keyword, clause_type in CLAUSE_KEYWORDS.items() 
             if keyword in text_lower]
    
    return found if found else ["genel"]

def parse_legal_text(full_text):
    # Ham OCR metnini Regex algoritmalarıyla analiz edip hukuki başlıklara (Madde, Fıkra vb.) göre hiyerarşik ağaca dönüştürür.
    lines = full_text.split('\n')
    root = ChunkNode("Sözleşme Başlangıcı", level=0)
    stack = [root]
    
    pat_level_1 = re.compile(r'^\s*(?:BÖLÜM|KISIM)\s+[IVX0-9]+|^\s*(?:I|II|III|IV|V|VI|VII|VIII|IX|X)[\.\-\s]*(?:[A-ZĞÜŞİÖÇ]|$)')
    pat_level_2 = re.compile(r'^\s*(?:GEÇİCİ\s+)?MADDE\s+\d+', flags=re.IGNORECASE)
    pat_level_3 = re.compile(r'^\s*\d+(?:\.\d+)*[\.\-\s]*(?:[A-ZĞÜŞİÖÇ]|$)')
    pat_level_4 = re.compile(r'^\s*[a-z][\)\-]\s+')
    
    current_node = root

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        level = 0
        title_match = ""
        
        if pat_level_1.match(line_clean):
            level = 1
            title_match = line_clean
        elif pat_level_2.match(line_clean):
            level = 2
            title_match = line_clean
        elif pat_level_3.match(line_clean) and len(line_clean.split()) < 10:
            level = 3
            title_match = line_clean
        elif pat_level_4.match(line_clean):
            level = 4
            match = pat_level_4.match(line_clean)
            title_match = match.group().strip()
            line_clean = line_clean[match.end():].strip()
            
        if level > 0:
            new_node = ChunkNode(title=title_match, level=level, content=line_clean if level == 4 else "")
            while len(stack) > 1 and stack[-1].level >= level:
                stack.pop()
            stack[-1].children.append(new_node)
            stack.append(new_node)
            current_node = new_node
        else:
            current_node.content += (" " if current_node.content else "") + line_clean

    return root

def flatten_chunks(node, parent_title=""):
    # Ağacı RAG (Vektör Veritabanı) formatı için düz bir listeye çevirir. 10 karakter altı boşlukları atlar.
    chunks = []
    current_title = f"{parent_title} > {node.title}" if parent_title and node.level > 0 else node.title
    
    if node.content and len(node.content) > 60:
        chunks.append({
            "metadata": {
                "hierarchy": current_title,
                "level": node.level,
                "clause_type": detect_clause_type(node.content)
            },
            "text": node.title + "\n" + node.content
        })
        
    for child in node.children:
        chunks.extend(flatten_chunks(child, current_title))
        
    return chunks
