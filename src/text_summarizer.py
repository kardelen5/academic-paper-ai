from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import transformers
import logging

# Çirkin Hugging Face uyarılarını (kırmızı yazıları) tamamen susturuyoruz
transformers.logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

class MultiModelSummarizer:
    def __init__(self):
        print("\n[🧠 SİSTEM] Flan-T5-LARGE Modeli Çekirdek API ile Yükleniyor...")
        model_name = "google/flan-t5-large"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def summarize(self, text: str, method="abstractive_formal", min_length=50, max_length=250) -> str:
        
        # PROMPT GÜNCELLENDİ: Modele açıkça "Kısa ve öz yaz (100-150 kelime)" diyoruz.
        prompt = (
            "Summarize the following academic text concisely (around 100-150 words). "
            "Focus strictly on the research methodology, algorithms, and final results. "
            "Do NOT include any author names, university names, or publication dates. \n\n"
            f"Text: {text}"
        )
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,   # Hard-limit (Maksimum Token - Yaklaşık 180 Kelime)
            min_length=50,               # Alt sınırı düşürdük, model kısa bitirirse zorla uzatmasın
            do_sample=False,             
            num_beams=4,                 
            repetition_penalty=2.0,      
            no_repeat_ngram_size=3       
            # length_penalty SİLİNDİ! Artık destan yazmaya çalışmayacak.
        )
        
        final_summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # GÜVENLİK SÜBABI: Eğer model sınıra çarpıp cümleyi yarım keserse, son noktadan (.) sonrasını atar!
        if '.' in final_summary:
            final_summary = final_summary.rsplit('.', 1)[0] + '.'
            
        return final_summary