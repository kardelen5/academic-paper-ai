import streamlit as st
import os
from gtts import gTTS
from deep_translator import GoogleTranslator

# Kendi yazdığın pipeline dosyasından ajanını içeri aktarıyoruz
from agentic_pipeline import ResearchAgent 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Research Assistant", page_icon="🧠", layout="wide")

# Proje Başlığı (Jüri için şık bir karşılama)
st.title("🧠 Yapay Zeka Tabanlı Makale Özetleme Asistanı")
st.markdown("Uygulamalı Yapay Sinir Ağları dersi için geliştirilmiş RAG mimarili çok dilli asistan.")
st.divider()

# Dinamik Dil Sözlüğü
diller = {
    "Türkçe": "tr",
    "Almanca": "de",
    "Fransızca": "fr",
    "İspanyolca": "es",
    "İtalyanca": "it",
    "Rusça": "ru"
}

# --- ARAYÜZ TASARIMI (2 Kolonlu Yapı) ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🔍 Arama Parametreleri")
    konu = st.text_input("Araştırma Konusu", placeholder="Örn: Deep Learning in Finance")
    must_input = st.text_input("Zorunlu Kelimeler", placeholder="Örn: prediction, market")
    should_input = st.text_input("Opsiyonel Kelimeler", placeholder="Örn: transformer")
    
    st.divider()
    st.header("⚙️ Çıktı Ayarları")
    # Kullanıcının dil seçimi
    secilen_dil_adi = st.selectbox("Çeviri Dili Seçin", list(diller.keys()))
    hedef_dil_kodu = diller[secilen_dil_adi]
    
    # Başlatma Butonu
    baslat = st.button("🚀 Araştırmayı Başlat", use_container_width=True)

with col2:
    if baslat and konu:
        # Spinner: İşlem bitene kadar dönen yükleme animasyonu
        with st.spinner("Kütüphaneler taranıyor ve yapay zeka makaleleri değerlendiriyor... (Lütfen bekleyin)"):
            
            # 1. Kelime filtreleme ayarlarını oluştur
            keywords_config = {}
            if must_input.strip():
                for kw in must_input.split(","):
                    if kw.strip(): keywords_config[kw.strip().lower()] = "MUST"
            if should_input.strip():
                for kw in should_input.split(","):
                    if kw.strip(): keywords_config[kw.strip().lower()] = "SHOULD"

            try:
                # 2. Senin gerçek yapay zeka ajanını (Cross-Encoder) çalıştır
                agent = ResearchAgent()
                uygun_makaleler = agent.search_and_score(query=konu, keywords_config=keywords_config, max_results=15, threshold=50.0)
                
                if uygun_makaleler:
                    # En yüksek puanı alan (ilk sıradaki) makaleyi seçiyoruz
                    secilen_makale = uygun_makaleler[0]
                    makale_basligi = secilen_makale.get("title", "Bilinmeyen Başlık")
                    makale_linki = secilen_makale.get("pdf_url", "#")
                    makale_kaynagi = secilen_makale.get("source", "Bilinmeyen Kaynak")
                    
                    # 3. Arayüze makale bilgisini ve PDF butonu ekle
                    st.success(f"📚 **Seçilen Makale:** {makale_basligi} ({makale_kaynagi})")
                    if makale_linki and makale_linki != "#":
                        st.link_button("🔗 Makalenin Orijinal PDF'ine Git", makale_linki)

                    # Makalenin orijinal özetini çek (Temsili metin kaldırıldı)
                    final_summary = secilen_makale.get("abstract", "Özet metni bulunamadı.")
                    
                    # 4. İngilizce Özeti Ekrana Bas
                    st.subheader("📄 Orijinal Özet (İngilizce)")
                    st.info(final_summary)

                    # 5. Seçilen Dile Çevir ve Ekrana Bas
                    st.subheader(f"🌐 Çeviri ({secilen_dil_adi})")
                    translated_summary = GoogleTranslator(source='en', target=hedef_dil_kodu).translate(final_summary)
                    st.success(translated_summary)

                    # 6. Ses Dosyası Oluştur ve Web'de Oynat
                    st.subheader("🎧 Sesli Dinleme")
                    try:
                        # Sesin dili kullanıcının seçtiği hedef dile (hedef_dil_kodu) ayarlandı
                        tts = gTTS(text=translated_summary, lang=hedef_dil_kodu, slow=False)
                        ses_dosyasi = "web_podcast.mp3"
                        tts.save(ses_dosyasi)
                        
                        # Streamlit'in müzik çaları ile sayfaya göm
                        st.audio(ses_dosyasi, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"Ses oluşturulurken bir hata meydana geldi: {e}")

                else:
                    st.warning("Bu kriterlere uygun, %50 barajını geçen makale bulunamadı. Lütfen daha genel terimler deneyin.")

            except Exception as e:
                st.error(f"Sistem çalışırken kritik bir hata oluştu: {e}")
                
    elif baslat and not konu:
        st.warning("Lütfen arama yapmak için bir araştırma konusu girin.")