from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import clean_text, remove_references_section

# 1. PDF dosyasının yolunu belirt (sample.pdf'in data/pdfs içinde olduğundan eminiz)
pdf_path = "data/pdfs/sample.pdf"

print("1. Aşama: PDF'den metin ayıklanıyor...")
raw = extract_text_from_pdf(pdf_path)
import os
print(f"Şu anki konum: {os.getcwd()}")
print(f"Dosya orada mı?: {os.path.exists(pdf_path)}")
if raw:
    print(f"Başarılı! Ham metin uzunluğu: {len(raw)} karakter.")
    
    print("\n2. Aşama: Referanslar bölümü temizleniyor...")
    # Önce referansları kesiyoruz (yeni satırlar henüz duruyorken)
    without_ref = remove_references_section(raw)
    
    print("3. Aşama: Metin temizleme (boşluklar, tireler) yapılıyor...")
    # Sonra genel temizliği yapıyoruz
    final_text = clean_text(without_ref)
    
    print("\n" + "="*50)
    print("TEMİZLENMİŞ VE DÜZENLENMİŞ METİN (İlk 1000 Karakter):")
    print("="*50)
    print(final_text[:1000])
    print("\n" + "="*50)
    print(f"İşlem tamamlandı. Final karakter sayısı: {len(final_text)}")
else:
    print("HATA: PDF metni okunamadı. Lütfen 'data/pdfs/sample.pdf' dosyasını kontrol et.")