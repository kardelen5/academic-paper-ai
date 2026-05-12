import re

def clean_text(text: str) -> str:
    """
    RAG motoruna gitmeden önce metindeki telif haklarını, yazar bilgilerini, 
    dergi isimlerini ve alakasız yasal uyarıları temizler.
    """
    #URL'leri, DOI linklerini ve E-postaları sil
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    text = re.sub(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', '', text, flags=re.IGNORECASE)

    # Akademik Yayıncıların ve Yazarların Klasik Gürültü Metinleri
    noise_patterns = [
        r"Dean\s?&\s?Francis",
        r"Research Article", 
        r"Volume\s?\d+,?\s?Issue\s?\d+", 
        r"Journal of.*?(?=\n)",
        r"Page \d+ of \d+",
        r"Published online.*?(?=\n)",
        r"(?:Department|Dept\.) of.*?(?=\n|Abstract|Introduction)",
        r"(?:University|College|Institute|Faculty) of.*?(?=\n|Abstract|Introduction)",
        r"Corresponding author.*?(?=\n)",
        r"ORCID:.*?(?=\s|\n)",
        r"Keywords:.*?(?=\n|Introduction)",
        r"Permission to make digital or hard copies.*?fee\.",
        r"Copyrights for components of this work.*?honored\.",
        r"Abstracting with credit is permitted\.",
        r"To copy otherwise, or republish.*?fee\.",
        r"CCS CONCEPTS\s*•?\s*Computing methodologies.*?(?=\n|[A-Z][a-z])",
        r"ACM Reference Format:",
        r"IEEE Transactions on.*?Vol\..*?\d{4}",
        r"Findings of the Association for Computational Linguistics.*?\d{4}"
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    #Sembol ve sayı [1, 2] gibi
    text = re.sub(r'\[\d+(,\s*\d+)*\]', '', text)
    
    #Gereksiz boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def remove_references_section(text: str) -> str:

    pattern = re.compile(r'(?i)(?:\n|\r|^)\s*(\d*\.?\s*(?:references|bibliography|literature cited|acknowledgments|acknowledgements))[\.\:\s]*(?:\n|\r|$)', re.IGNORECASE)
    
    match = pattern.search(text)
    if match:
        print(f"\nKaynakça/Teşekkür bölümü bulundu ve ATILDI")
        text = text[:match.start()]
    else:
        #Eğer başlığı bulamazsa, makalenin son %20'sini acımadan kesip atar.
        kesim_noktasi = int(len(text) * 0.80)
        print("\nKaynakça/Teşekkür bölümü bulunamadı! Makalenin son %20'si kesiliyor.")
        text = text[:kesim_noktasi]
        
    return text


def normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def extract_abstract(text: str) -> str:
    """
    Makalenin içinden 'Abstract' kısmını bulur ve çıkarır.
    Bu kısım RAG mimarimizde 'Arama Sorgusu' olarak kullanılacaktır.
    """
    pattern = re.compile(r'(?i)abstract[\.\:]?\s*(.*?)(?=(?:keywords|introduction|1\.\s+introduction|\n\n\n|$))', re.DOTALL)
    match = pattern.search(text)
    
    if match:
        extracted = match.group(1).strip()
        # Yakalanan özetin içindeki yazar kalıntılarını tekrar temizle
        return clean_text(extracted)
            
    print("[UYARI] Abstract başlığı net bulunamadı, makalenin ilk 200 kelimesi sorgu olarak kullanılacak.")
    return " ".join(text.split()[:200])