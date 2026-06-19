from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import transformers
import logging

transformers.logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

class MultiModelSummarizer:
    def __init__(self):
        print("\n---Özetleme Motoru Başlatılıyor---")
        model_name = "google/flan-t5-large"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    def summarize(self, text: str, min_length=90, max_length=250) -> str:
        
        prompt = (
            "You are an expert academic AI assistant. Your task is to write a highly detailed, "
            "comprehensive, and accurate technical summary of the provided research text. "
            "Keep the summary between 90 and 250 words.\n\n"
            "CRITICAL RULES:\n"
            "1. STRICTLY EXCLUDE any References, Bibliography, Acknowledgments, Citations (e.g., [1], [2]), "
            "author names, emails, or university affiliations.\n"
            "2. Focus strictly on the core methodology, proposed architecture, datasets, and final results.\n"
            "3. DO NOT hallucinate or invent information. Base your summary EXACTLY and ONLY on the provided text.\n\n"
            f"Research Text:\n{text}\n\n"
            "Academic Summary:"
        )
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            min_new_tokens=min_length, 
            length_penalty=2.0,       
            do_sample=False,        
            num_beams=4,            
            repetition_penalty=2.0, 
            no_repeat_ngram_size=3  
        )
        
        final_summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        sentences = final_summary.split('. ')
        bad_keywords = ["University", "School", "Dept", "Faculty", "Author", "Vol.", "No.", "Published", "Edited", "WANG", "GUO", "et al", "References", "Acknowledgement", "Copyright", "Press", "199", "200", "201", "202"] 
        
        filtered_sentences = [s for s in sentences if not any(word.lower() in s.lower() for word in bad_keywords)]
        
        if len(filtered_sentences) > 0:
            final_summary = ". ".join(filtered_sentences).strip()
            if not final_summary.endswith('.'): final_summary += '.'
        
        if '. ' in final_summary:
            final_summary = final_summary.rsplit('. ', 1)[0] + '.'
            
        return final_summary