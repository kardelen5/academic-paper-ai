import re

def clean_text(text: str) -> str:
    #Ham metni temizler ve düzenler.

    if not text:
        return ""
        
    # PyMuPDF'in araya boşluk attığı tireli kelimeleri birleştirir
    text = re.sub(r'-\s+', '', text)
    
    # 1. Satır sonlarını birleştir
    lines = text.split('\n')
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()  # Sağdaki boşlukları temizle
        
        # Eğer satır tire ile bitiyorsa, sonraki satırla birleştir (tireyi kaldır)
        if line.endswith('-') and i + 1 < len(lines):
            # Tire ile biten satır: sonraki satırın başındaki boşlukları silip ekle
            next_line = lines[i + 1].lstrip()
            combined = line[:-1] + next_line  # tireyi çıkar
            processed_lines.append(combined)
            i += 2  # iki satırı işledik
        else:
            # Normal satır: boşluk eklemeden ekle (satır sonu boşluğa dönüşecek)
            processed_lines.append(line)
            i += 1
    
    # Şimdi satırları boşluk ile birleştir (her satır sonu boşluk olsun)
    text = ' '.join(processed_lines)
    
    # 2. Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text)  # Birden çok boşluk yerine tek boşluk
    
    # 3. Satır başındaki ve sonundaki boşlukları temizle
    text = text.strip()
    
    text = re.sub(r'\.{2,}', '.', text)  # 2'den fazla nokta -> tek nokta
    
    return text


def remove_references_section(text: str) -> str:
    """
    Metindeki referanslar bölümünü kaldırmaya çalışır.
    Basit bir yaklaşım: "References" veya "Kaynaklar" gibi bir başlıktan sonrasını keser.
    """
    patterns = [
        r'\nREFERENCES\s*\n',
        r'\nReferences\s*\n',
        r'\nKAYNAKLAR\s*\n',
        r'\nKaynaklar\s*\n',
        r'\nBIBLIOGRAPHY\s*\n',
        r'\nBibliography\s*\n',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            text = text[:match.start()]
            break
    return text


def normalize_whitespace(text: str) -> str:
    #Sadece boşluk normalizasyonu yapar
    return re.sub(r'\s+', ' ', text).strip()