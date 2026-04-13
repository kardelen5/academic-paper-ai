import os
from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import remove_references_section, clean_text, extract_abstract
from src.chunker import chunk_text
from src.similarity import SimilarityEngine
from src.text_summarizer import MultiModelSummarizer

pdf_yolu = "data/pdfs/sample.pdf"

if not os.path.exists(pdf_yolu):
    print(f"HATA: {pdf_yolu} bulunamadı!")
else:
    print("1. PDF Okunuyor ve Temizleniyor...")
    raw_text = extract_text_from_pdf(pdf_yolu)
    
   
    abstract_text = extract_abstract(raw_text)
    print(f"\n[BİLGİ] Abstract başarıyla çıkarıldı! (Uzunluk: {len(abstract_text.split())} kelime)")
    
    
    clean_txt = clean_text(remove_references_section(raw_text))
    
    
    chunks = chunk_text(clean_txt, chunk_size=30, overlap=3)
    print(f"\n2. Makale {len(chunks)} parçaya bölündü.")

    #RAG arama motoru devreye giriyor
    print("\n3. ARAMA MOTORU DEVREYE GİRİYOR (RAG Mimarisi)...")

    # Benzerlik motorundan bir nesne oluştur
    search_engine = SimilarityEngine()

    # Abstract'ı sorgu olarak kullan, chunks listesi içinde en benzer ilk 3 parçayı bul.
    # Bu parçalar, orijinal makalenin abstract ile en alakalı kısımlarıdır.
    top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=3)
    

    #Bu en alakalı parçaları tek bir metin halinde birleştir
    focused_text = " ".join(top_chunks)

    
    print("\n4. NİHAİ ÖZETLEME YAPILIYOR (Sadece Filtrelenmiş Metin Kullanılarak)...")
    app = MultiModelSummarizer()
    
    # Özetlenecek metin focused_text
    final_summary = app.summarize(focused_text, method="abstractive_formal", min_length=150, max_length=250)

    print("\n" + "="*70)
    print("BÜTÜN MAKALENİN RAG DESTEKLİ NİHAİ ÖZETİ (ABSTRACTIVE FORMAL):")
    print("="*70 + "\n")
    print(final_summary)
    print("\n" + "="*70)
    print(f"Toplam Özet Uzunluğu: {len(final_summary.split())} kelime.")