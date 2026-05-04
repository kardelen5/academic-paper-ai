"""
Agentic RAG Mimarisi: 'Kesin Filtre' (Hard Filter) ve Cross-Encoder ile çalışan Ajan.
"""
import numpy as np
from sentence_transformers import CrossEncoder
from src.arxiv_fetcher import ArxivFetcher

class ResearchAgent:
    def __init__(self):
        print("[SİSTEM] Yapay Zeka Araştırma Ajanı (Research Agent) başlatılıyor...")
        self.fetcher = ArxivFetcher()
        
        print("⚖️ Yargıç Model (Cross-Encoder) yükleniyor: ms-marco-MiniLM-L-6-v2...")
        self.confidence_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    # DİKKAT: focus_word parametresi geri geldi ve max_results 10'a çıkarıldı!
    def search_and_score(self, query: str, focus_word: str = "", max_results: int = 10, threshold: float = 50.0):
        """
        1. ArXiv'den makaleleri çeker.
        2. KESİN FİLTRE: focus_word varsa, içermeyen makaleleri anında siler.
        3. Cross-Encoder ile Confidence (Eminlik) skoru üretir.
        """
        # ArXiv'den daha geniş bir havuz (10 makale) çekiyoruz
        papers = self.fetcher.search_papers(query, max_results)

        if not papers:
            print("[UYARI] ArXiv'den makale çekilemedi.")
            return []

        # -------------------------------------------------------------
        # 1. KESİN FİLTRE (HARD FILTER / GATEKEEPER) AŞAMASI
        # -------------------------------------------------------------
        if focus_word:
            print(f"\n[🛡️ KAPI GÖREVLİSİ] İçinde '{focus_word}' geçmeyen makaleler acımasızca eleniyor...")
            gecerli_makaleler = []
            for paper in papers:
                # Odak kelimesi makalenin özetinde VEYA başlığında geçiyorsa içeri al
                if focus_word.lower() in paper["abstract"].lower() or focus_word.lower() in paper["title"].lower():
                    gecerli_makaleler.append(paper)
            
            papers = gecerli_makaleler
            print(f"[🛡️ FİLTRE SONUCU] Kriteri karşılayan makale sayısı: {len(papers)}")

        if not papers:
            print(f"[UYARI] '{focus_word}' kelimesini içeren hiçbir makale bulunamadı. Lütfen aramayı değiştirin.")
            return []

        # -------------------------------------------------------------
        # 2. CROSS-ENCODER İLE EMİNLİK PUANLAMASI
        # -------------------------------------------------------------
        print("\n[AJAN DÜŞÜNÜYOR] Kalan makale özetleri okunuyor ve 'Eminlik Derecesi' hesaplanıyor...")

        filtered_papers = []

        for paper in papers:
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
            print(f"[Eminlik Skoru: %{p['similarity_score']:.1f}] {p['title']}")
            
        return filtered_papers