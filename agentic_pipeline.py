"""
AGENTIC RAG BÜYÜK FİNALİ:
1. Konuyu arat ve en iyi makaleyi seç.
2. PDF'i otomatik indir.
3. RAG özetleme pipeline'ından geçir.
"""
import os
import requests
import nltk
from src.research_agent import ResearchAgent
from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import remove_references_section, clean_text, extract_abstract
from src.chunker import chunk_text
from src.similarity import SimilarityEngine
from src.text_summarizer import MultiModelSummarizer

# NLTK Kontrolü
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def download_pdf(pdf_url: str, save_path: str):
    """ArXiv PDF'ini bilgisayara indirir."""
    print(f"\nPDF İndiriliyor: {pdf_url} ...")
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("Makale başarıyla indirildi!")
        return True
    except Exception as e:
        print(f"PDF indirilemedi: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("ARAŞTIRMA ASİSTANI BAŞLATILDI")
    print("="*70)

    
    print("\nLütfen araştırmak istediğiniz konuyu ve özel olarak odaklanılmasını istediğiniz kelimeyi girin.")
    konu = input("Araştırma Konusu (Örn: Large Language Models in Healthcare): ")
    odak_kelimesi = input("Odak/Ağırlık Verilecek Kelime (Örn: Healthcare) İstemiyorsanız boş bırakın: ")
    

    agent = ResearchAgent()
    uygun_makaleler = agent.search_and_score(query=konu, focus_word=odak_kelimesi, max_results=5, threshold=0.45)

    if not uygun_makaleler:
        print("\n Uygun makale bulunamadı. Lütfen arama kriterlerini değiştirin.")
        exit()

    print("\n" + "*"*70)
    print("EN İYİ 3 MAKALENİN İŞLEME DÖNGÜSÜ BAŞLIYOR")
    print("*"*70)

    # KLASÖR HAZIRLIĞI
    pdf_klasoru = "data/pdfs"
    os.makedirs(pdf_klasoru, exist_ok=True)

    # SADECE İLK 3 MAKALEYİ AL (Eğer 3'ten az varsa, olanları al)
    hedef_makaleler = uygun_makaleler[:3] 

    for i, makale in enumerate(hedef_makaleler):
        print(f"\n---İŞLENEN MAKALE {i+1} / {len(hedef_makaleler)} ---")
        print(f"Başlık: {makale['title']} (Skor: %{makale['similarity_score']*100:.1f})")

        # Her PDF için farklı bir isim oluştur
        hedef_pdf_yolu = os.path.join(pdf_klasoru, f"temp_paper_{i}.pdf")
        indirme_linki = makale['pdf_url'] + ".pdf" 
        
        # PDF'i İndir
        if download_pdf(indirme_linki, hedef_pdf_yolu):
            try:
                # Makaleyi Oku ve Temizle
                raw_text = extract_text_from_pdf(hedef_pdf_yolu)
                abstract_text = extract_abstract(raw_text)
                
                if len(abstract_text.split()) < 20: 
                    abstract_text = makale['abstract']
                    
                clean_txt = clean_text(remove_references_section(raw_text))
                chunks = chunk_text(clean_txt, chunk_size=30, overlap=3)
                
                # RAG Motoru
                search_engine = SimilarityEngine()
                top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=3)
                focused_text = " ".join(top_chunks)

                # Özetleme (BART)
                app = MultiModelSummarizer()
                final_summary = app.summarize(focused_text, method="abstractive_formal", min_length=150, max_length=250)

                # Çıktı
                print(f"\n>>> ÖZET ({i+1}):")
                print(final_summary)

            except Exception as e:
                print(f"Makale {i+1} özetlenirken sorun oluştu: {e}")

            finally:
                if os.path.exists(hedef_pdf_yolu):
                    os.remove(hedef_pdf_yolu)
                    print(f"Sistemdeki geçici PDF dosyası silindi ({hedef_pdf_yolu})")

    print("\n" + "="*70)
    print("TÜM İŞLEMLER TAMAMLANDI. SİSTEM TEMİZ DURUMDA.")
    print("="*70)