import re

def clean_text(text: str) -> str:
    

    if not text:
        return ""
        
    #Satır sonundaki tire + boşluk desenini kaldır
    text = re.sub(r'-\s+', '', text)
    
    
    lines = text.split('\n')
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()  
        
        
        if line.endswith('-') and i + 1 < len(lines):
            
            next_line = lines[i + 1].lstrip()
            combined = line[:-1] + next_line  
            processed_lines.append(combined)
            i += 2  
        else:
            
            processed_lines.append(line)
            i += 1
    
    #İşlenmiş satırları tek bir metin haline getir
    text = ' '.join(processed_lines)
    
    #Tüm çoklu boşlukları tek boşluk yap
    text = re.sub(r'\s+', ' ', text)  
    
    #Metnin başındaki ve sonundaki boşlukları temizle
    text = text.strip()
    
    #Art arda gelen noktaları tek nokta yap
    text = re.sub(r'\.{2,}', '.', text) 
    
    return text


def remove_references_section(text: str) -> str:
    """
    Metindeki referanslar bölümünü kaldırmaya çalışır.

    """
    
    pattern = re.compile(r'(?:^\s*|\n)(?:\d+\.\s*)?(references|kaynaklar|bibliography)[\.\:]?\s*(?:$|\n)', re.IGNORECASE)
    
    match = pattern.search(text)
    if match:
        
        print(f"\nReferanslar bölümü başarıyla bulundu ve atıldı! (Yakalanan Başlık: '{match.group(1).capitalize()}')")
        text = text[:match.start()]
        #Metni baştan referans başlığının başladığı yere kadar kes (referanslar kısmını at)
    else:
        print("\n[UYARI] Referanslar başlığı bulunamadı, metin kesilmedi.")
        
    return text


def normalize_whitespace(text: str) -> str:
    
    return re.sub(r'\s+', ' ', text).strip()

def extract_abstract(text: str) -> str:
    """
    Makalenin içinden 'Abstract' kısmını bulur ve çıkarır.
    Bu kısım RAG mimarimizde 'Arama Sorgusu' olarak kullanılacaktır.
    """
    
    import re
    pattern = re.compile(r'(?i)abstract[\.\:]?\s*(.*?)(?=(?:keywords|introduction|1\.\s+introduction|\n\n\n|$))', re.DOTALL)
    match = pattern.search(text)
    
    if match:
        extracted = match.group(1).strip()
        
        if len(extracted.split()) > 20:
            return extracted
            
    
    print("[UYARI] Abstract başlığı net bulunamadı, makalenin ilk 200 kelimesi sorgu olarak kullanılacak.")
    return " ".join(text.split()[:200])