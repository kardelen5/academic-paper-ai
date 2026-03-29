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
    
    chunks = chunk_text(clean_txt, chunk_size=20, overlap=2)
    
    print(f"\n2. Makale başarıyla {len(chunks)} parçaya bölündü.")
    print("3. TÜM MAKALE EXTRACTIVE INFORMAL (Twitter RoBERTa) ile özetleniyor...\n")

    app = MultiModelSummarizer()
    final_summary_parts = []

    for i, chunk in enumerate(chunks):
        print(f" -> Parça {i+1}/{len(chunks)} taranıyor ve Twitter algoritmasına göre cümleler seçiliyor...")
        # Metindeki "sosyal medya etkileşimi" en yüksek olan cümleyi cımbızlayacak
        chunk_summary = app.summarize(chunk, method="extractive_informal")
        
        if chunk_summary:
            final_summary_parts.append(chunk_summary)

    tam_ozet = " ".join(final_summary_parts)

    print("\n" + "="*70)
    print("BÜTÜN MAKALENİN BİRLEŞTİRİLMİŞ ÖZETİ (EXTRACTIVE INFORMAL - Twitter):")
    print("="*70 + "\n")
    print(tam_ozet)
    print("\n" + "="*70)
    print(f"Toplam Özet Uzunluğu: {len(tam_ozet.split())} kelime.")