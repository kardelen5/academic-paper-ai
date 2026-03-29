import os
from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import remove_references_section, clean_text
from src.chunker import chunk_text
from src.text_summarizer import MultiModelSummarizer

pdf_yolu = "data/pdfs/sample.pdf"

if not os.path.exists(pdf_yolu):
    print(f"HATA: {pdf_yolu} bulunamadı!")
else:
    print("1. PDF Okunuyor ve Temizleniyor...")
    raw_text = extract_text_from_pdf(pdf_yolu)
    
    if "Abstract" in raw_text:
        raw_text = raw_text[raw_text.find("Abstract"):]
        
    clean_txt = clean_text(remove_references_section(raw_text))
    
    # Makaleyi yine 20'şer cümlelik parçalara bölüyoruz
    chunks = chunk_text(clean_txt, chunk_size=20, overlap=2)
    
    print(f"\n2. Makale başarıyla {len(chunks)} parçaya (chunk) bölündü.")
    print("3. TÜM MAKALE EXTRACTIVE (SciBERT) ile özetleniyor...\n")

    app = MultiModelSummarizer()
    final_summary_parts = []

    for i, chunk in enumerate(chunks):
        print(f" -> Parça {i+1}/{len(chunks)} taranıyor ve en önemli cümleler cımbızlanıyor...")
        
        # Extractive modelimiz verdiğimiz metnin %30'unu (en önemli kısımlarını) orijinal haliyle çekecek
        chunk_summary = app.summarize(chunk, method="extractive_formal")
        
        if chunk_summary:
            final_summary_parts.append(chunk_summary)

    # Cımbızlanan tüm cümleleri birleştiriyoruz
    tam_ozet = " ".join(final_summary_parts)

    print("\n" + "="*70)
    print("BÜTÜN MAKALENİN BİRLEŞTİRİLMİŞ UZUN ÖZETİ (EXTRACTIVE FORMAL - SciBERT):")
    print("="*70 + "\n")
    print(tam_ozet)
    print("\n" + "="*70)
    print(f"Toplam Özet Uzunluğu: {len(tam_ozet.split())} kelime.")