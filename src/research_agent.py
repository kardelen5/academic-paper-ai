"""
Agentic RAG Mimarisi: Multi-Source (ArXiv + OpenAlex), Hard Filter ve Cross-Encoder.
"""
import numpy as np
from sentence_transformers import CrossEncoder
from src.arxiv_fetcher import ArxivFetcher
from src.openalex_fetcher import OpenAlexFetcher

class ResearchAgent:
    def __init__(self):
        print("---Araştırma başlatılıyor---")
        self.arxiv_fetcher = ArxivFetcher()
        self.oa_fetcher = OpenAlexFetcher()
        
        print("Cross-Encoder yükleniyor") #ms-marco-MiniLM-L-6-v2
        self.confidence_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def search_and_score(self, query: str, focus_word: str = "", max_results: int = 15, threshold: float = 50.0):
        print("\nKütüphaneler taranıyor")
        
        arxiv_papers = self.arxiv_fetcher.search_papers(query, max_results)
        for p in arxiv_papers: p["source"] = "ArXiv" 
            
        oa_papers = self.oa_fetcher.search_papers(query, max_results)

        all_papers = arxiv_papers + oa_papers

        if not all_papers:
            print("[UYARI] Hiçbir kaynaktan makale çekilemedi.")
            return []
            
        print(f"\nToplam {len(all_papers)} makale toplandı (ArXiv: {len(arxiv_papers)}, OpenAlex: {len(oa_papers)})")

        if focus_word:
            print(f"\nİçinde '{focus_word}' geçmeyen makaleler eleniyor!")
            gecerli_makaleler = []
            for paper in all_papers:
                if focus_word.lower() in paper["abstract"].lower() or focus_word.lower() in paper["title"].lower():
                    gecerli_makaleler.append(paper)
            
            all_papers = gecerli_makaleler
            print(f"Kriteri karşılayan makale sayısı: {len(all_papers)}")

        if not all_papers:
            print(f"[UYARI] '{focus_word}' kelimesini içeren makale bulunamadı.")
            return []

        print("\nKalan makale özetleri okunuyor.")

        filtered_papers = []
        for paper in all_papers:
            ham_skor = self.confidence_model.predict([query, paper["abstract"]])
            confidence_score = (1 / (1 + np.exp(-ham_skor))) * 100
            paper["similarity_score"] = float(confidence_score)

            if confidence_score >= threshold:
                filtered_papers.append(paper)

        filtered_papers = sorted(filtered_papers, key=lambda x: x["similarity_score"], reverse=True)

        print("\n" + "="*70)
        print(f"KARAR SONUCU: {len(filtered_papers)} makale güven eşiğini (%{threshold}) geçti.")
        print("="*70)
        
        for p in filtered_papers:
            print(f"[Eminlik: %{p['similarity_score']:.1f}] [{p['source']}] {p['title']}")
            
        return filtered_papers