import os
import nltk
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

    print("\n3. ARAMA MOTORU DEVREYE GİRİYOR (RAG Mimarisi)...")
    search_engine = SimilarityEngine()
    top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=3)

    focused_text = " ".join(top_chunks)

    print("\n4. NİHAİ ÖZETLEME YAPILIYOR (SciBERT - Cımbızlayıcı)...")
    app = MultiModelSummarizer()
    
    
    raw_summary = app.summarize(focused_text, method="extractive_formal")
    sentences = nltk.sent_tokenize(raw_summary)

    # Önem sıralamasını abstract'a benzerliğe göre yeniden yap
    print("   -> Cümleler önem puanına göre sıralanıyor...")
    ranked_sentences = search_engine.find_top_chunks(query=abstract_text, chunks=sentences, top_k=len(sentences))
    # Her cümleyi abstract ile karşılaştır, benzerlik skoruna göre büyükten küçüğe sırala.
    # top_k = len(sentences) ile tüm cümleleri sıralanmış olarak al.
    
    selected_sentences = []
    current_word_count = 0

    for cumle in ranked_sentences:
        kelime_sayisi = len(cumle.split())
        if current_word_count + kelime_sayisi <= 150:
            selected_sentences.append(cumle)
            current_word_count += kelime_sayisi


    final_sentences = [cumle for cumle in sentences if cumle in selected_sentences]
    
    final_summary = " ".join(final_sentences)
    if not final_summary.strip() and sentences:
        final_summary = sentences[0]

    print("\n" + "="*70)
    print("BÜTÜN MAKALENİN RAG DESTEKLİ NİHAİ ÖZETİ (EXTRACTIVE FORMAL - SciBERT):")
    print("="*70 + "\n")
    print(final_summary)
    print("\n" + "="*70)
    print(f"Toplam Özet Uzunluğu: {len(final_summary.split())} kelime.")