# Otonom Akademik Makale Özetleme Sistemi (Agentic RAG)

Bu proje, Uygulamalı Yapay Sinir Ağları dersi kapsamında geliştirilmiş; literatür tarama sürecini otomatize eden, iki aşamalı getirme (Two-Stage Retrieval) mimarisiyle çalışan ajan tabanlı bir RAG sistemidir.

## Geliştirici Bilgileri (Bireysel Proje)

Bu proje takım çalışması olarak değil, uçtan uca tek bir öğrenci tarafından bireysel olarak tasarlanmış ve geliştirilmiştir:

- **Kardelen Nur Kargacı** - 23040101024 (İstanbul Topkapı Üniversitesi, Bilgisayar Mühendisliği 3. Sınıf)

## Sistem Gereksinimleri

- Python 3.8 veya üzeri
- Aktif internet bağlantısı (API üzerinden otonom literatür taraması ve nöral çeviri işlemleri için gereklidir)

## Kurulum ve Çalıştırma Talimatları

Sistemi yerel ortamınızda çalıştırmak için aşağıdaki adımları sırasıyla VS Code terminalinizde uygulayın:

**1. Bağımlılıkların (Kütüphanelerin) Yüklenmesi:**
Projenin ana dizininde bir terminal açın ve gerekli tüm Python kütüphanelerini yüklemek için şu komutu çalıştırın:

```bash
pip install -r requirements.txt
```

**2. NLTK Dil Paketinin Kurulumu:**
Sistemin PDF içerisindeki metinleri bağlamı koparmadan ayırabilmesi için NLTK `punkt` paketinin indirilmesi gerekir. Terminale şunu yazıp çalıştırın:

```bash
python -c "import nltk; nltk.download('punkt')"
```

**3. Uygulamanın Başlatılması:**
Kurulumlar tamamlandıktan sonra Streamlit arayüzünü ayağa kaldırmak için terminalde şu komutu çalıştırın:

```bash
streamlit run web_app.py
```

**4. Arayüze Erişim:**
Yukarıdaki komut çalıştıktan sonra varsayılan web tarayıcınız otonom olarak açılacaktır. Açılmazsa, tarayıcınızın adres çubuğuna giderek `http://localhost:8501` yazıp sisteme erişebilirsiniz.
