import fitz  # PyMuPDF
import PyPDF2
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Verilen PDF dosyasındaki metni çıkarır.
    Önce PyMuPDF dener, hata alırsa PyPDF2'ye geçer.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")
    
    text = ""
    
    
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            text_blocks = [b[4] for b in blocks if b[6] == 0]
            
            for block in text_blocks:
                cleaned_block = block.replace('\n', ' ').strip()
                if cleaned_block:
                    text += cleaned_block + "\n\n"
        doc.close()
    except Exception as e:
        print(f"Uyarı: PyMuPDF bu PDF'i okurken zorlandı ({e}).")
        text = "" 
        
    
    if not text.strip():
        print("Uyarı: PDF sıkıştırma hatası var. Alternatif okuyucu (PyPDF2) devreye giriyor...")
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Kritik Hata: PDF her iki motorla da okunamadı! Bozuk dosya olabilir: {e}")
            
    return text.strip()

if __name__ == "__main__":
    sample_pdf = "data/pdfs/sample.pdf"
    if os.path.exists(sample_pdf):
        content = extract_text_from_pdf(sample_pdf)
        print("Çıkarılan metnin ilk 500 karakteri:\n")
        print(content[:500])
    else:
        print("Test için PDF bulunamadı.")