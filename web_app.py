import streamlit as st
import os
import requests
from gtts import gTTS
from deep_translator import GoogleTranslator

# --- SENİN YAZDIĞIN BÜTÜN MODÜLLERİ (BEYNİ) İÇERİ AKTARIYORUZ ---
from src.research_agent import ResearchAgent
from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import remove_references_section, clean_text, extract_abstract
from src.chunker import chunk_text
from src.similarity import SimilarityEngine
from src.text_summarizer import MultiModelSummarizer

# Terminal kodundaki PDF indirme fonksiyonunun aynısı
def download_pdf(pdf_url: str, save_path: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(pdf_url, headers=headers, timeout=10)
        response.raise_for_status()
        if "text/html" in response.headers.get("Content-Type", ""):
            return False
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception:
        return False

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Research Assistant", page_icon="🧠", layout="wide")

st.title("🧠 Yapay Zeka Tabanlı Makale Özetleme Asistanı")
st.markdown("Uygulamalı Yapay Sinir Ağları dersi için geliştirilmiş RAG mimarili çok dilli asistan.")
st.divider()

diller = {
    "Türkçe": "tr",
    "Almanca": "de",
    "Fransızca": "fr",
    "İspanyolca": "es",
    "İtalyanca": "it",
    "Rusça": "ru"
}

col1, col2 = st.columns([1, 2])

with col1:
    st.header("🔍 Arama Parametreleri")
    konu = st.text_input("Araştırma Konusu", placeholder="Örn: Deep Learning in Finance")
    must_input = st.text_input("Zorunlu Kelimeler", placeholder="Örn: prediction, market")
    should_input = st.text_input("Opsiyonel Kelimeler", placeholder="Örn: transformer")
    
    st.divider()
    st.header("⚙️ Çıktı Ayarları")
    secilen_dil_adi = st.selectbox("Çeviri Dili Seçin", list(diller.keys()))
    hedef_dil_kodu = diller[secilen_dil_adi]
    
    baslat = st.button("🚀 Araştırmayı Başlat", use_container_width=True)

with col2:
    if baslat and konu:
        with st.spinner("Kütüphaneler taranıyor ve uygun makaleler aranıyor..."):
            keywords_config = {}
            if must_input.strip():
                for kw in must_input.split(","):
                    if kw.strip(): keywords_config[kw.strip().lower()] = "MUST"
            if should_input.strip():
                for kw in should_input.split(","):
                    if kw.strip(): keywords_config[kw.strip().lower()] = "SHOULD"

            agent = ResearchAgent()
            uygun_makaleler = agent.search_and_score(query=konu, keywords_config=keywords_config, max_results=15, threshold=50.0)

        if not uygun_makaleler:
            st.error("Uygun makale bulunamadı. Lütfen daha genel terimler deneyin.")
        else:
            st.success(f"Eşiği geçen toplam {len(uygun_makaleler)} makale bulundu. En iyi 3 tanesi RAG mimarisine sokuluyor...")
            
            pdf_klasoru = "data/pdfs"
            os.makedirs(pdf_klasoru, exist_ok=True)
            
            basarili_islem = 0
            hedef_islem = 3 # Tıpkı terminaldeki gibi 3 makale hedefi
            
            # --- TERMİNALDEKİ DÖNGÜNÜN BİREBİR AYNISI ---
            for i, makale in enumerate(uygun_makaleler):
                if basarili_islem >= hedef_islem:
                    break
                    
                makale_basligi = makale.get("title", "Bilinmeyen Başlık")
                indirme_linki = makale.get('pdf_url', '')
                if not indirme_linki.endswith('.pdf'): indirme_linki += ".pdf"
                hedef_pdf_yolu = os.path.join(pdf_klasoru, f"temp_paper_{i}.pdf")
                
                # Streamlit "Expander" ile her makaleyi kendi kutusu içinde gösteriyoruz
                with st.expander(f"📚 {basarili_islem + 1}. Makale: {makale_basligi}", expanded=True):
                    
                    with st.spinner("PDF İndiriliyor, Parçalanıyor ve Özetleniyor..."):
                        islem_basarili_mi = False
                        
                        if download_pdf(indirme_linki, hedef_pdf_yolu):
                            try:
                                # 1. PDF Okuma ve Temizleme
                                raw_text = extract_text_from_pdf(hedef_pdf_yolu)
                                if len(raw_text.split()) < 50: raise ValueError("PDF okunamayacak formatta")
                                clean_txt = clean_text(remove_references_section(raw_text))
                                
                                # 2. Chunking (Parçalama)
                                # Eski Hali: chunks = chunk_text(clean_txt, chunk_size=150, overlap=20)
                                # Yeni Hali:
                                chunks = chunk_text(clean_txt, chunk_size=150, overlap=30)    
                                
                                # 3. Benzerlik Ölçümü (Cosine Similarity)
                                search_engine = SimilarityEngine()
                                abstract_text = extract_abstract(raw_text)
                                if len(abstract_text.split()) < 20: abstract_text = makale.get('abstract', '')
                                # Eski Hali: top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=5)
                                # Yeni Hali:
                                top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=4)
                                focused_text = " ".join(top_chunks)
                                
                                # 4. Yapay Zeka Özetleme Motoru
                                app = MultiModelSummarizer()
                                final_summary = app.summarize(focused_text, min_length=90, max_length=250)
                                
                                # 4. Yapay Zeka Özetleme Motoru
                                app = MultiModelSummarizer()
                                final_summary = app.summarize(focused_text, min_length=90, max_length=250)
                                
                                # YENİ BAŞARI MESAJI BURAYA GELECEK
                                st.success(f"✅Makalenin en alakalı bölümleri filtrelendi ve modellendi.")
                                
                                # 5. Çıktıları Ekrana Basma
                                
                                # 5. Çıktıları Ekrana Basma
                                st.markdown("**📄 Yapay Zeka Özeti (İngilizce)**")
                                st.write(final_summary)

                                translated_summary = GoogleTranslator(source='en', target=hedef_dil_kodu).translate(final_summary)
                                st.markdown(f"**🌐 Çeviri ({secilen_dil_adi})**")
                                st.success(translated_summary)

                                # 6. Ses Dosyası Oluşturma
                                try:
                                    tts = gTTS(text=translated_summary, lang=hedef_dil_kodu, slow=False)
                                    ses_dosyasi = f"web_podcast_{i}.mp3"
                                    tts.save(ses_dosyasi)
                                    st.audio(ses_dosyasi, format="audio/mp3")
                                except Exception as e:
                                    st.warning(f"Ses oluşturulurken hata: {e}")
                                    
                                # Makale Linki Butonu
                                if makale.get("pdf_url"):
                                    st.link_button("🔗 Orijinal PDF'e Git", makale["pdf_url"])
                                    
                                islem_basarili_mi = True
                                
                            except Exception as e:
                                st.warning(f"İçerik okunamadı veya özetlenemedi ({e}). Sonraki makaleye geçiliyor...")
                        else:
                            st.warning("Makale linki doğrudan bir PDF içermiyor. Sonraki makaleye geçiliyor...")
                            
                        # İşlem durumuna göre başarılı sayacı artır ve dosyayı sil
                        if islem_basarili_mi:
                            basarili_islem += 1
                        if os.path.exists(hedef_pdf_yolu):
                            os.remove(hedef_pdf_yolu)

            if basarili_islem == 0:
                st.error("Havuzdaki makalelerin hiçbirinden geçerli bir PDF çıkarılamadı ve özetlenemedi.")
            elif basarili_islem < hedef_islem:
                st.warning(f"Yalnızca {basarili_islem} adet makale başarılı bir şekilde özetlenebildi.")
            else:
                st.success("Tüm işlemler başarıyla tamamlandı!")

    elif baslat and not konu:
        st.warning("Lütfen arama yapmak için bir araştırma konusu girin.")