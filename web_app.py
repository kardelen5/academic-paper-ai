import streamlit as st
import os
import requests
from gtts import gTTS
from deep_translator import GoogleTranslator
from src.research_agent import ResearchAgent
from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import remove_references_section, clean_text, extract_abstract
from src.chunker import chunk_text
from src.similarity import SimilarityEngine
from src.text_summarizer import MultiModelSummarizer

st.set_page_config(page_title="Özetleme Sistemi", layout="centered")

st.markdown("""
    <style>
    .stApp {background-color: #fcfcfd;}
    h1 {color: #4a306d !important; text-align: center !important;}
    .block-container {max-width: 800px !important; padding-top: 2rem;}
    .stButton>button {background-color: #6a4c93 !important; color: white !important;}
    </style>
""", unsafe_allow_html=True)

st.title("📄Özetleme Sistemi")

konu = st.text_input("Araştırma Konusu", placeholder="Örn: Generative AI for 3D Character Modeling")
col1, col2 = st.columns(2)
with col1:
    must_input = st.text_input("Zorunlu Kelimeler", placeholder="Örn: Generative, 3D İstemiyorsanız boş bırakıp Enter'a basın")
with col2:
    should_input = st.text_input("Opsiyonel Kelimeler", placeholder="Virgülle ayırın. İstemiyorsanız boş bırakıp Enter'a basın")

diller = {
    "Türkçe": "tr",
    "Almanca": "de",
    "Fransızca": "fr",
    "İspanyolca": "es",
    "İtalyanca": "it",
    "Rusça": "ru"
}
secilen_dil_adi = st.selectbox("Çeviri Dili", list(diller.keys()))
hedef_dil_kodu = diller[secilen_dil_adi]

baslat = st.button("Araştırmayı Başlat", use_container_width=True)
st.divider()

def download_pdf(pdf_url, save_path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(pdf_url, headers=headers, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f: f.write(response.content)
        return True
    except: return False

if baslat and konu:
    with st.spinner("Makaleler aranıyor..."):
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
        st.error("Uygun makale bulunamadı.")
    else:
        pdf_klasoru = "data/pdfs"
        os.makedirs(pdf_klasoru, exist_ok=True)
        basarili_islem = 0
        
        for i, makale in enumerate(uygun_makaleler):
            if basarili_islem >= 3: break
            
            makale_basligi = makale.get("title", "Bilinmeyen Başlık")
            indirme_linki = makale.get('pdf_url', '')
            if not indirme_linki.endswith('.pdf'): indirme_linki += ".pdf"
            hedef_pdf_yolu = os.path.join(pdf_klasoru, f"temp_{i}.pdf")
            
            if not download_pdf(indirme_linki, hedef_pdf_yolu):
                continue 

            with st.expander(f"📚 {basarili_islem + 1}. Makale: {makale_basligi}", expanded=True):
                try:
                    raw_text = extract_text_from_pdf(hedef_pdf_yolu)
                    clean_txt = clean_text(remove_references_section(raw_text))
                    chunks = chunk_text(clean_txt, chunk_size=150, overlap=30)
                    
                    search_engine = SimilarityEngine()
                    abstract_text = extract_abstract(raw_text)
                    if len(abstract_text.split()) < 20: 
                        abstract_text = makale['abstract']
                        
                    top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=4)
                    focused_text = " ".join(top_chunks)
                    
                    app = MultiModelSummarizer()
                    final_summary = app.summarize(focused_text, min_length=90, max_length=250)
                    
                    st.success(f"Özet Başarılı")
                    st.markdown("**📄 İngilizce Özet**")
                    st.write(final_summary)

                    translated = GoogleTranslator(source='en', target=hedef_dil_kodu).translate(final_summary)
                    st.markdown(f"**🌐 Çeviri ({secilen_dil_adi})**")
                    st.write(translated)

                    tts = gTTS(text=translated, lang=hedef_dil_kodu, slow=False)
                    ses_dosyasi = f"podcast_{i}.mp3"
                    tts.save(ses_dosyasi)
                    st.audio(ses_dosyasi, format="audio/mp3")
                    
                    if makale.get("pdf_url"): st.link_button("🔗 Orijinal PDF", makale["pdf_url"])
                    basarili_islem += 1
                except Exception as e: st.warning(f"İşlenemedi: {e}")
                
                if os.path.exists(hedef_pdf_yolu): os.remove(hedef_pdf_yolu)