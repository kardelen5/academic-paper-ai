import re

def clean_text(text: str) -> str:
    """
    RAG motoruna gitmeden önce metindeki telif haklarını, dergi isimlerini, 
    linkleri ve alakasız yasal uyarıları temizler.
    """
    # URL'leri, DOI linklerini ve E-postaları sil
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    text = re.sub(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', '', text, flags=re.IGNORECASE)

    # Akademik Yayıncıların (ACM, IEEE vb.) Klasik Telif Metinleri
    boilerplate_patterns = [
        r"Permission to make digital or hard copies.*?fee\.",
        r"Copyrights for components of this work.*?honored\.",
        r"Copyrights for components of the work.*?honored\.",
        r"Abstracting with credit is permitted\.",
        r"To copy otherwise, or republish.*?fee\.",
        r"CCS CONCEPTS\s*•?\s*Computing methodologies.*?(?=\n|[A-Z][a-z])", # ACM'nin CCS Concepts kısmını yakalar
        r"ACM Reference Format:",
        r"IEEE Transactions on.*?Vol\..*?\d{4}",
        r"Findings of the Association for Computational Linguistics.*?\d{4}",
        r"For confidential support call.*?samaritans\.org\.?"
    ]
    
    # Büyük/küçük harf duyarsız, satır atlamalarını kapsa
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    # Sembol ve sayı temizliği
    text = re.sub(r'\[\d+(,\s*\d+)*\]', '', text)
    
    # Silinen metinler yüzünden oluşan dev boşlukları tek boşluğa indirir
    text = re.sub(r'\s+', ' ', text).strip()
    
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