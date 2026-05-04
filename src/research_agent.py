"""
Agentic RAG Mimarisi: İnternetten veri çeken ve benzerlik skoruyla filtreleyen Ajan.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.arxiv_fetcher import ArxivFetcher
from src.embedding import TextEmbedder

class ResearchAgent:
    def __init__(self):
        print("Araştırma Ajanı başlatılıyor")
        self.fetcher = ArxivFetcher()
        self.embedder = TextEmbedder()

    def search_and_score(self, query: str, focus_word: str = "", max_results: int = 5, threshold: float = 0.40):
        """
        1. ArXiv'den makaleleri çeker.
        2. Her makalenin Abstract'ı ile aranan query arasındaki Kosinüs Benzerliğini hesaplar.
        3. Eşik değerinin altındakileri eler.
        """
        papers = self.fetcher.search_papers(query, max_results)

        if not papers:
            print("[UYARI] Ajan makale bulamadı.")
            return []

        print("\n Makale özetleri okunuyor ve anlamsal benzerlik hesaplanıyor")
        query_vector = self.embedder.get_embedding(query).reshape(1, -1)
        filtered_papers = []

        for paper in papers:
            abstract_vector = self.embedder.get_embedding(paper["abstract"]).reshape(1, -1)
            similarity_score = cosine_similarity(query_vector, abstract_vector)[0][0]
            
            if focus_word:
                # Eğer odak kelimesi abstract içinde geçiyorsa skoru arttır
                if focus_word.lower() in paper["abstract"].lower():
                    print(f" '{focus_word}' kelimesi bulundu. Skora +0.15 ekleniyor: {paper['title']}")
                    similarity_score += 0.15 
                else:
                    # İçinde hiç geçmiyorsa biraz cezalandır
                    similarity_score -= 0.05

            paper["similarity_score"] = similarity_score

            if similarity_score >= threshold:
                filtered_papers.append(paper)

        filtered_papers = sorted(filtered_papers, key=lambda x: x["similarity_score"], reverse=True)

        print("\n" + "="*70)
        print(f"{len(papers)} makale incelendi, {len(filtered_papers)} tanesi eşik değerini (%{threshold*100:.0f}) geçti.")
        print("="*70)
        
        for p in filtered_papers:
            print(f"[Skor: %{p['similarity_score']*100:.1f}] {p['title']}")
            
        return filtered_papers

if __name__ == "__main__":
    agent = ResearchAgent()
    test_konusu = "Large Language Models in Healthcare"
    
    # 5 makale getir, ama sadece %40 ve üzeri benzerlikte olanları bana sun
    uygun_makaleler = agent.search_and_score(query=test_konusu, max_results=5, threshold=0.40)