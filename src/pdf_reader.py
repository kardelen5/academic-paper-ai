import fitz  # PyMuPDF
import PyPDF2
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Verilen PDF dosyasındaki metni çıkarır.
    Akademik makaleler için DÜZENE DUYARLI (Layout-Aware) çift sütun okuması yapar.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")
    
    text = ""
    
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            
            # Sayfanın genişliğini ve orta noktasını (x ekseni) bul
            page_width = page.rect.width
            mid_x = page_width / 2
            
            full_width_blocks = []
            left_blocks = []
            right_blocks = []
            
            for b in blocks:
                if b[6] != 0: continue  # Sadece metin bloklarını al
                
                # Koordinatlar: x0 (sol), y0 (üst), x1 (sağ), y1 (alt)
                x0, y0, x1, y1, block_text, block_num, block_type = b
                
                if x0 < mid_x and x1 > mid_x and (x1 - x0) > (page_width * 0.6):
                    full_width_blocks.append(b)

                elif x1 <= mid_x + 40: # +40 piksel esneme payı
                    left_blocks.append(b)

                else:
                    right_blocks.append(b)
            
            # Her grubu kendi içinde yukarıdan aşağıya sırala
            full_width_blocks.sort(key=lambda b: b[1])
            left_blocks.sort(key=lambda b: b[1])
            right_blocks.sort(key=lambda b: b[1])
            
            sorted_blocks = full_width_blocks + left_blocks + right_blocks
            
            for block in sorted_blocks:
                cleaned_block = block[4].replace('\n', ' ').strip()
                if cleaned_block:
                    text += cleaned_block + "\n\n"
                    
        doc.close()
    except Exception as e:
        print(f"Uyarı: PyMuPDF bu PDF'i okurken zorlandı ({e}).")
        text = "" 
        
    if not text.strip():
        print("Uyarı: Alternatif okuyucu (PyPDF2) devreye giriyor...")
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Hata: PDF her iki motorla da okunamadı! Bozuk dosya olabilir: {e}")
            
    return text.strip()