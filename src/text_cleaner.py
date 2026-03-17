"""
PDF'den çıkarılan ham metni temizleme ve düzenleme modülü.
Kullanım: clean_text(raw_text) -> str
"""

import re

def clean_text(text: str) -> str:
    """
    Ham metni temizler ve düzenler.
    
    1. Satır sonlarını birleştirir (tire ile biten satırlar bitişik, diğerleri boşluk).
    2. Fazla boşlukları ve satır başlarını temizler.
    3. Gereksiz karakterleri filtreler.
    
    Args:
        text (str): Temizlenecek ham metin.
    
    Returns:
        str: Temizlenmiş metin.
    """
    if not text:
        return ""
    
    # 1. Satır sonlarını birleştir
    # Önce satır sonlarını geçici bir işaretçi ile değiştirip tire kontrolü yapalım.
    # Daha sağlam bir yöntem: Satırları tek tek işle.
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
    text = re.sub(r'\s+', ' ', text)  # Birden çok boşluk -> tek boşluk
    
    # 3. Satır başındaki ve sonundaki boşlukları temizle
    text = text.strip()
    
    # 4. İsteğe bağlı: Bazı özel karakterleri temizle (noktalama işaretlerini koru)
    # Örneğin, kontrol karakterlerini temizle (ASCII olmayanları silme, Türkçe için gerekli)
    # Sadece yazdırılabilir karakterleri tutmak istersen:
    # text = ''.join(c for c in text if c.isprintable())
    
    # 5. Birden çok noktalama işaretini düzelt (örneğin ... -> tek nokta)
    # Bu kısım isteğe bağlı, basit bir regex:
    text = re.sub(r'\.{2,}', '.', text)  # 2'den fazla nokta -> tek nokta
    
    return text


def remove_references_section(text: str) -> str:
    """
    Metindeki referanslar bölümünü kaldırmaya çalışır.
    Basit bir yaklaşım: "References" veya "Kaynaklar" gibi bir başlıktan sonrasını keser.
    Not: Akademik makalelerde referanslar genelde sonda olur, ama her zaman olmayabilir.
    """
    # Türkçe ve İngilizce yaygın referans başlıkları
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
    """Sadece boşluk normalizasyonu yapar (yardımcı fonksiyon)."""
    return re.sub(r'\s+', ' ', text).strip()


if __name__ == "__main__":
    sample = "Bu bir test metnidir.\nBu satırda tire yok.\nAncak bu satır tire ile bitiyor-\nve devam ediyor.\n\n\nÇoklu satır sonu.\n\nReferences\nBurası silinmeli."
    
    # SIRALAMAYI DEĞİŞTİRDİK:
    # Önce referansları atıyoruz (çünkü \n işaretleri hala duruyor)
    without_ref = remove_references_section(sample) 
    
    # Sonra temizliyoruz
    cleaned = clean_text(without_ref)
    
    print("Sonuç:\n", cleaned)