"""
Metin parçaları arasında anlamsal benzerlik (Cosine Similarity) hesaplayan modül.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.embedding import TextEmbedder

class SimilarityEngine:
    def __init__(self):
        
        self.embedder = TextEmbedder()

    def find_top_chunks(self, query: str, chunks: list[str], top_k: int = 3) -> list[str]:
        """
        Verilen bir sorguya (Abstract) en çok benzeyen ilk 'top_k' parçayı bulur.
        """
        if not query or not chunks:
            return []

       
        query_vector = self.embedder.get_embedding(query)
        query_vector = query_vector.reshape(1, -1)

        
        chunk_vectors = self.embedder.get_embeddings(chunks)

        
        similarities = cosine_similarity(query_vector, chunk_vectors)[0]

        
        top_indices = np.argsort(similarities)[::-1][:top_k]

        print(f"\n[BİLGİ] Abstract'a en çok benzeyen {top_k} parça filtrelendi!")
        for i, idx in enumerate(top_indices):
            print(f" -> Seçilen Parça (Orijinal İndeks: {idx}) - Benzerlik Skoru: %{similarities[idx]*100:.1f}")

        
        top_chunks = [chunks[idx] for idx in top_indices]
        return top_chunks