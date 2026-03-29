"""
Makale özetleme modülü.
1. Abstractive - Formal (BART CNN)
2. Abstractive - Informal (BART SAMSum)
3. Extractive - Formal (SciBERT) - Custom Algorithm
4. Extractive - Informal (Twitter RoBERTa) - Custom Algorithm
"""

import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity # Cosine similarity vektör benzerliği ölçmek için
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
import nltk

class MultiModelSummarizer:
    def __init__(self):
        self.models = {
            "abstractive_formal": None,
            "abstractive_informal": None,
            "extractive_formal": None,
            "extractive_informal": None
        }
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_abstractive_formal(self):

        if self.models["abstractive_formal"] is None:  # Eğer model daha önce yüklenmemişse yükle
            print("Abstractive Formal Model (BART) yükleniyor")
            tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn") # Tokenizer metni modele uygun sayılara çevirir
            model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn").to(self.device)
            self.models["abstractive_formal"] = {"tokenizer": tokenizer, "model": model}

        return self.models["abstractive_formal"]

    def _load_abstractive_informal(self):

        if self.models["abstractive_informal"] is None:
            print("Abstractive Informal Model (SAMSum) yükleniyor")
            tokenizer = AutoTokenizer.from_pretrained("philschmid/bart-large-cnn-samsum")
            model = AutoModelForSeq2SeqLM.from_pretrained("philschmid/bart-large-cnn-samsum").to(self.device)
            self.models["abstractive_informal"] = {"tokenizer": tokenizer, "model": model}

        return self.models["abstractive_informal"]

    def _load_extractive_formal(self):

        if self.models["extractive_formal"] is None:
            print("Extractive Formal Model (SciBERT) yükleniyor")
            tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
            model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased').to(self.device)
            self.models["extractive_formal"] = {"tokenizer": tokenizer, "model": model}

        return self.models["extractive_formal"]

    def _load_extractive_informal(self):

        if self.models["extractive_informal"] is None:
            print("Extractive Informal Model (Twitter) yükleniyor...")
            tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base')
            model = AutoModel.from_pretrained('cardiffnlp/twitter-roberta-base').to(self.device)
            self.models["extractive_informal"] = {"tokenizer": tokenizer, "model": model}

        return self.models["extractive_informal"]

    
    # EXTRACTIVE ÖZET ALGORİTMASI
    def _custom_extractive_summarize(self, text: str, model_dict: dict, ratio: float = 0.3) -> str:

        tokenizer = model_dict["tokenizer"]
        model = model_dict["model"]
        
        # Metni cümlelere böl
        sentences = nltk.sent_tokenize(text)
        num_sentences = max(1, int(len(sentences) * ratio)) #Kaç cümle seçileceğini belirle
        
        if len(sentences) <= num_sentences:
            return text

        inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt", max_length=512).to(self.device)
        
        # Modeli çalıştır
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Her cümlenin embedding'ini al
        sentence_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

        # Tüm cümlelerin ortalaması
        document_embedding = np.mean(sentence_embeddings, axis=0).reshape(1, -1)

        # Her cümlenin dokümana benzerliği
        similarities = cosine_similarity(sentence_embeddings, document_embedding).flatten()

        # En yüksek similarity'ye sahip cümleleri seç
        top_indices = similarities.argsort()[-num_sentences:][::-1]

        # Orijinal sıralamaya geri getir
        top_indices.sort()
        
         # Seçilen cümleleri birleştir
        summary = " ".join([sentences[i] for i in top_indices])
        return summary
    

    # ANA ÖZET FONKSİYONU

    # Çok kısa metinse özetleme yapma
    def summarize(self, text: str, method: str = "abstractive_formal", min_length=50, max_length=150) -> str:
        if not text or len(text.split()) < 20:
            return text

        try:
            if method in ["abstractive_formal", "abstractive_informal"]:
                if method == "abstractive_formal":
                    model_dict = self._load_abstractive_formal()
                else:
                    model_dict = self._load_abstractive_informal()
                
                tokenizer = model_dict["tokenizer"]
                model = model_dict["model"]

                # Text'i modele uygun sayılara çevir
                inputs = tokenizer(text, max_length=1024, truncation=True, return_tensors="pt").to(self.device)

                # Özet uzunluğunu dinamik belirle
                adjusted_max = min(max_length, max(min_length + 10, int(len(text.split()) * 0.8)))

                # Burada modelden text generate etmesini istiyoruz 
                summary_ids = model.generate(
                    inputs["input_ids"],
                    max_length=adjusted_max,
                    min_length=min_length,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
                
                summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                return summary

            elif method == "extractive_formal":
                model_dict = self._load_extractive_formal()
                return self._custom_extractive_summarize(text, model_dict, ratio=0.3)

            elif method == "extractive_informal":
                model_dict = self._load_extractive_informal()
                return self._custom_extractive_summarize(text, model_dict, ratio=0.3)
                
            else:
                raise ValueError("Geçersiz özetleme metodu!")

        except Exception as e:
            print(f"Özetleme sırasında hata: {e}")
            return ""
        

# ---- TEST BLOĞU  ----
if __name__ == "__main__":
    test_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.
    The term "artificial intelligence" had previously been used to describe machines that mimic and display "human" cognitive skills that are associated with the human mind, such as "learning" and "problem-solving". This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated.
    """
    
    print("Sistem başlatılıyor, 4 model de sırayla test edilecek...\n")
    app = MultiModelSummarizer()
    
    print("==================================================")
    print("1. ABSTRACTIVE - FORMAL (BART Large CNN)")
    print("Beklenti: Metni okuyup, akademik dille kendi cümlelerini kurması.")
    print("--------------------------------------------------")
    print("Sonuç:", app.summarize(test_text, method="abstractive_formal", min_length=20, max_length=60))
    
    print("\n==================================================")
    print("2. ABSTRACTIVE - INFORMAL (BART SAMSum)")
    print("Beklenti: Metni okuyup, günlük konuşma formatına yakın bir dille özetlemesi.")
    print("--------------------------------------------------")
    print("Sonuç:", app.summarize(test_text, method="abstractive_informal", min_length=20, max_length=60))
    
    print("\n==================================================")
    print("3. EXTRACTIVE - FORMAL (SciBERT)")
    print("Beklenti: Matematiksel olarak akademik ana fikre en yakın, en resmi cümleyi cımbızla çekmesi.")
    print("--------------------------------------------------")
    print("Sonuç:", app.summarize(test_text, method="extractive_formal"))
    
    print("\n==================================================")
    print("4. EXTRACTIVE - INFORMAL (Twitter RoBERTa)")
    print("Beklenti: Bir sosyal medya algoritmasının dikkatini çekecek kelimeler barındıran cümleyi seçmesi.")
    print("--------------------------------------------------")
    print("Sonuç:", app.summarize(test_text, method="extractive_informal"))
    print("==================================================")