from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import clean_text, remove_references_section
from src.chunker import chunk_text

# 1. PDF'den metni çek
print("1. PDF okunuyor...")
raw = extract_text_from_pdf("data/pdfs/sample.pdf")

if raw:
    # 2. Metni temizle
    print("2. Metin temizleniyor...")
    cleaned = clean_text(raw)
    cleaned = remove_references_section(cleaned)

    # 3. Metni parçalara (chunk) böl
    print("3. Metin parçalara ayrılıyor...")
    # chunk_size=10: her parça 10 cümle, overlap=2: 2 cümle ortak
    chunks = chunk_text(cleaned, chunk_size=10, overlap=2)

    print(f"\n✅ Toplam {len(chunks)} parça oluşturuldu.\n")

    # 4. Parçaları ekrana bas (İlk 3 parçayı görelim)
    for i, c in enumerate(chunks[:3]):
        print(f"--- Parça {i+1} ({len(c.split())} kelime) ---")
        print(c[:300] + "...") # İlk 300 karakteri göster
        print("-" * 40)
else:
    print("❌ HATA: PDF okunamadı! 'data/pdfs/sample.pdf' dosyasını kontrol et.")