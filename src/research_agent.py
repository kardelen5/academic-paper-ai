"""
Agentic RAG Mimarisi: Multi-Source (ArXiv + OpenAlex), Hard Filter ve Cross-Encoder.
"""
import numpy as np
from sentence_transformers import CrossEncoder
from src.arxiv_fetcher import ArxivFetcher
from src.openalex_fetcher import OpenAlexFetcher
from src.ssrn_fetcher import SSRNFetcher

class ResearchAgent:
    def __init__(self):
        print("---Araştırma başlatılıyor---")
        self.arxiv_fetcher = ArxivFetcher()
        self.oa_fetcher = OpenAlexFetcher()
        self.ssrn_fetcher = SSRNFetcher()
        
        print("Cross-Encoder yükleniyor") #ms-marco-MiniLM-L-6-v2
        self.confidence_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def search_and_score(self, query: str, keywords_config: dict = None, max_results: int = 15, threshold: float = 50.0):
        print("\nKütüphaneler taranıyor")
        
        arxiv_papers = self.arxiv_fetcher.search_papers(query, max_results)
        for p in arxiv_papers: p["source"] = "ArXiv" 
            
        oa_papers = self.oa_fetcher.search_papers(query, max_results)
        ssrn_papers = self.ssrn_fetcher.search_papers(query, max_results)

        all_papers = arxiv_papers + oa_papers + ssrn_papers
        
        if not all_papers:
            print("[UYARI] Hiçbir kaynaktan makale çekilemedi.")
            return []
            
        print(f"\nToplam {len(all_papers)} makale toplandı (ArXiv: {len(arxiv_papers)}, OpenAlex: {len(oa_papers)})")

        
        if keywords_config:
            print("\nKelime filtresi uygulanıyor...")
            gecerli_makaleler = []
            
            for paper in all_papers:
                
                text_to_search = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
                
                # Kesin içersin kontrolü
                must_keywords = [k for k, v in keywords_config.items() if v == "MUST"]
                is_missing_must = False
                for m_kw in must_keywords:
                    if m_kw not in text_to_search:
                        is_missing_must = True
                        break
                
                if is_missing_must:
                    continue
                
                # İçerse iyi olur kontrolü
                found_shoulds = []
                should_keywords = [k for k, v in keywords_config.items() if v == "SHOULD"]
                for s_kw in should_keywords:
                    if s_kw in text_to_search:
                        found_shoulds.append(s_kw)
                
                paper['found_optional_keywords'] = found_shoulds
                gecerli_makaleler.append(paper)
            
            all_papers = gecerli_makaleler
            print(f"Kriteri karşılayan makale sayısı: {len(all_papers)}")

        if not all_papers:
            print(f"[UYARI] Zorunlu kriterleri karşılayan makale bulunamadı.")
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
            opt_kw_text = f" (Ekstra: {', '.join(p.get('found_optional_keywords', []))})" if p.get('found_optional_keywords') else ""
            print(f"[Eminlik: %{p['similarity_score']:.1f}] [{p['source']}] {p['title']}{opt_kw_text}")
            
        return filtered_papers