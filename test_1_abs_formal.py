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
    
    # Makaleyi 20'şer cümlelik parçalara bölüyoruz (Overlap=2 ile bağlam kopmasın diye)
    chunks = chunk_text(clean_txt, chunk_size=20, overlap=2)
    
    print(f"\n2. Makale başarıyla {len(chunks)} parçaya (chunk) bölündü.")
    print("3. TÜM MAKALE özetleniyor... (Bu işlem makalenin uzunluğuna göre birkaç dakika sürebilir, lütfen bekleyin)\n")

    app = MultiModelSummarizer()
    final_summary_parts = []

    # BÜTÜN PARÇALARI DÖNGÜYE SOKUYORUZ (Map-Reduce Mantığı)
    for i, chunk in enumerate(chunks):
        print(f" -> Parça {i+1}/{len(chunks)} işleniyor...")
        
        # Daha uzun özetler için parametreleri artırdık (min:60, max:200 kelime her parça için)
        chunk_summary = app.summarize(chunk, method="abstractive_formal", min_length=60, max_length=200)
        
        if chunk_summary:
            final_summary_parts.append(chunk_summary)

    # Tüm parçaların özetlerini birleştiriyoruz
    tam_ozet = " ".join(final_summary_parts)

    print("\n" + "="*60)
    print("BÜTÜN MAKALENİN BİRLEŞTİRİLMİŞ UZUN ÖZETİ (ABSTRACTIVE FORMAL):")
    print("="*60 + "\n")
    print(tam_ozet)
    print("\n" + "="*60)
    print(f"Toplam Özet Uzunluğu: {len(tam_ozet.split())} kelime.")