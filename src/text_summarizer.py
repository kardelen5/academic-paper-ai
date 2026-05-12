from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import transformers
import logging

# Hugging Face uyarılarını sustur
transformers.logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

class MultiModelSummarizer:
    def __init__(self):
        print("\n---Özetleme Motoru Başlatılıyor---")
        model_name = "google/flan-t5-large"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def summarize(self, text: str, min_length=90, max_length=300) -> str:
        
        prompt = (
            "Task: Provide a technical summary of the research. Skip any biographical info.\n\n"
            "Example 1 (Bad Output): 'Paper by Alice Smith from Stanford University. This study explores...'\n"
            "Example 1 (Good Output): 'This study explores...'\n\n"
            "Example 2 (Bad Output): 'Vol. 10, No. 2, 2024. The authors discuss...'\n"
            "Example 2 (Good Output): 'The research discusses...'\n\n"
            f"Text to Process: {text}\n"
            "Summary:"
        )
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            min_length=min_length,
            do_sample=False,        #rastgelelik kapalı       
            num_beams=4,            #4 farklı cevaptan en iyisini seç           
            repetition_penalty=2.0, #aynı kelimeleri tekrar etmemesi için     
            no_repeat_ngram_size=3  #3 kelimelik tekrarları engelle     
        )
        
        final_summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        sentences = final_summary.split('. ')
        bad_keywords = ["University", "School", "Dept", "Faculty", "Author", "Vol.", "No.", "Published", "Edited", "WANG", "GUO"]
        
        # Eğer bir cümle yazar veya okul bilgisi içeriyorsa onu listeden çıkar
        filtered_sentences = [s for s in sentences if not any(word.lower() in s.lower() for word in bad_keywords)]
        
        # Eğer filtreleme her şeyi sildiyse orijinali kalsın, yoksa temizlenmiş hali
        if len(filtered_sentences) > 0:
            final_summary = ". ".join(filtered_sentences).strip()
            if not final_summary.endswith('.'): final_summary += '.'
        

        if '. ' in final_summary:
            final_summary = final_summary.rsplit('. ', 1)[0] + '.'
            
        return final_summary
            