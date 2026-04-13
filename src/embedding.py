"""
Metinleri matematiksel vektörlere (embedding) çeviren modül.
"""
from sentence_transformers import SentenceTransformer
import numpy as np

class TextEmbedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Hafif ve anlamsal arama (semantic search) için optimize edilmiş modeli yükler.
        """
        print(f" Embedding modeli yükleniyor: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: str) -> np.ndarray:
        """Tek bir metni (örneğin makalenin Abstract kısmını) vektöre çevirir."""
        if not text or not text.strip():
            raise ValueError("Vektöre çevrilecek metin boş olamaz.")
        return self.model.encode(text)

    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        """Makalenin parçalarını (chunk) toplu halde vektörlere çevirir."""
        if not texts:
            return np.array([])
        return self.model.encode(texts)