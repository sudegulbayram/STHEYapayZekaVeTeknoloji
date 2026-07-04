import re

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
    
    if node.content and len(node.content) > 10:
        chunks.append({
            "metadata": {"hierarchy": current_title, "level": node.level},
            "text": node.content
        })
        
    for child in node.children:
        chunks.extend(flatten_chunks(child, current_title))
        
    return chunks
