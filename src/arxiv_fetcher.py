"""
Ajanımızın ArXiv üzerinden literatür taraması yapmasını sağlayan modül.
"""
import arxiv

class ArxivFetcher:
    def __init__(self):
        self.client = arxiv.Client()

    def search_papers(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Kullanıcının girdiği konuya göre ArXiv'de arama yapar.
        En alakalı makalelerin Başlık, Abstract ve PDF linklerini döndürür.
        """
        print(f"\nArXiv'de '{query}' konusu için en alakalı makaleler aranıyor...")
        
        # Arama sorgusunu oluşturuyoruz
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance # konuya en uygun olanları getir
        )

        results = []
        try:
            # Sonuçları listeye topluyoruz
            all_results = list(self.client.results(search))
            
            for paper in all_results:
                # Makale bilgilerini sözlük formatında paketliyoruz
                paper_info = {
                    "title": paper.title,
                    "abstract": paper.summary.replace('\n', ' '),
                    "pdf_url": paper.pdf_url,
                    "authors": [author.name for author in paper.authors]
                }
                results.append(paper_info)
            
            if results:
                print(f" -> Başarılı: ArXiv'den {len(results)} adet makale çekildi.")
            else:
                print(" -> Uyarı: ArXiv'de ilgili makale bulunamadı.")
                
        except Exception as e:
            print(f"[HATA] ArXiv'den veri çekilirken hata oluştu: {e}")
            
        return results

if __name__ == "__main__":
    fetcher = ArxivFetcher()
    test_konusu = "Large Language Models in Healthcare"
    makaleler = fetcher.search_papers(test_konusu, max_results=15)