"""
PDF dosyalarından metin çıkarma modülü.
Kullanım: extract_text_from_pdf(pdf_path) -> str
"""

import PyPDF2
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Verilen PDF dosyasındaki tüm metni çıkarır.
    
    Args:
        pdf_path (str): PDF dosyasının yolu.
    
    Returns:
        str: Çıkarılan metin. Hata durumunda boş string dönebilir.
    
    Raises:
        FileNotFoundError: PDF dosyası bulunamazsa.
        PyPDF2.errors.PdfReadError: PDF okunamazsa (bozuk/şifreli).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")
    
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Şifre kontrolü (basit, şifresiz varsayıyoruz)
            if reader.is_encrypted:
                # Bazı PDF'ler boş şifre ile açılabilir, deneyelim
                try:
                    reader.decrypt('')
                except:
                    raise PyPDF2.errors.PdfReadError("PDF şifre korumalı ve açılamıyor.")
            
            # Tüm sayfaları dolaş
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        # Hata durumunda yeniden fırlat veya logla
        raise PyPDF2.errors.PdfReadError(f"PDF okunurken hata: {e}")
    
    return text.strip()


def extract_text_from_multiple_pdfs(pdf_paths: list) -> dict:
    """
    Birden çok PDF'den metin çıkarır.
    
    Args:
        pdf_paths (list): PDF dosya yollarının listesi.
    
    Returns:
        dict: {dosya_adı: metin} şeklinde sözlük.
    """
    results = {}
    for path in pdf_paths:
        try:
            text = extract_text_from_pdf(path)
            results[os.path.basename(path)] = text
        except Exception as e:
            results[os.path.basename(path)] = f"HATA: {e}"
    return results


# Basit bir test (modül doğrudan çalıştırılırsa)
if __name__ == "__main__":
    # Test için örnek bir PDF yolu (proje dizininde data/pdfs/sample.pdf olmalı)
    sample_pdf = "data/pdfs/sample.pdf"
    try:
        content = extract_text_from_pdf(sample_pdf)
        print("PDF içeriği (ilk 500 karakter):")
        print(content[:500])
    except Exception as e:
        print(f"Test başarısız: {e}")