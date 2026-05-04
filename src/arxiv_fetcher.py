"""
Ajanımızın ArXiv üzerinden literatür taraması yapmasını sağlayan modül.
"""
import arxiv

class ArxivFetcher:
    def __init__(self):
        # ArXiv API istemcisini başlatıyoruz
        self.client = arxiv.Client()

    def search_papers(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Kullanıcının girdiği konuya göre ArXiv'de arama yapar.
        En alakalı (Relevance) makalelerin Başlık, Abstract ve PDF linklerini döndürür.
        """
        print(f"\n[AJAN BİLGİSİ] ArXiv'de '{query}' konusu için en alakalı {max_results} makale aranıyor...")
        
        # Arama sorgusunu oluşturuyoruz
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance #konuya en uygun olanları getir
        )

        results = []
        try:
            for paper in self.client.results(search):
                # Makale bilgilerini sözlük formatında paketliyoruz
                paper_info = {
                    "title": paper.title,
                    "abstract": paper.summary.replace('\n', ' '),
                    "pdf_url": paper.pdf_url,
                    "authors": [author.name for author in paper.authors]
                }
                results.append(paper_info)
                print(f" -> Bulundu: {paper.title}")
                
        except Exception as e:
            print(f"[HATA] ArXiv'den veri çekilirken hata oluştu: {e}")
            
        return results


if __name__ == "__main__":
    
    fetcher = ArxivFetcher()
    
    test_konusu = "Large Language Models in Healthcare"
    makaleler = fetcher.search_papers(test_konusu, max_results=3)
    
    print("\n" + "="*50)
    print("ÖRNEK MAKALE ÇIKTISI:")
    print("="*50)
    if makaleler:
        ornek = makaleler[0]
        print(f"BAŞLIK: {ornek['title']}")
        print(f"YAZARLAR: {', '.join(ornek['authors'])}")
        print(f"PDF İNDİRME LİNKİ: {ornek['pdf_url']}")
        print(f"ABSTRACT: {ornek['abstract'][:250]}... (devamı var)")
    print("="*50)