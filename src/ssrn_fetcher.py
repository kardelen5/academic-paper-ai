import requests

class SSRNFetcher:
    """
    SSRN makalelerini çekmek için OpenAlex API'sini bir köprü (Facade) olarak kullanan modül.
    SSRN bot korumasına takılmadan yasal yollarla veri çekmeyi sağlar.
    """
    def __init__(self):
        self.base_url = "https://api.openalex.org/works"

    def search_papers(self, query: str, max_results: int = 5):
        print(f"\nSSRN Kütüphanesinde '{query}' aranıyor (OpenAlex Köprüsü ile)...")
        
        params = {
            "search": query,
            "filter": "primary_location.source.id:s4210172589", 
            "per-page": max_results,
            "mailto": "kardelen@example.com" 
        }
        
        papers = []
        max_deneme = 3 
        for deneme in range(max_deneme):
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("results", []):
                    pdf_url = item.get("primary_location", {}).get("pdf_url") or item.get("primary_location", {}).get("landing_page_url")
                    abstract_inverted = item.get("abstract_inverted_index")

                    if pdf_url and abstract_inverted:
                        words = []
                        for word, positions in abstract_inverted.items():
                            for pos in positions:
                                words.append((pos, word))
                        words.sort()
                        abstract_text = " ".join([word for pos, word in words])

                        papers.append({
                            "title": item.get("title", ""),
                            "abstract": abstract_text,
                            "pdf_url": pdf_url,
                            "source": "SSRN" 
                        })

                print(f" -> Başarılı: SSRN'den {len(papers)} adet pdf çekildi.")
                return papers 

            except requests.exceptions.Timeout:
                print(f"[UYARI] SSRN sunucusu yanıt vermekte gecikti. Yeniden deneniyor... ({deneme + 1}/{max_deneme})")
            except Exception as e:
                print(f"[HATA] SSRN bağlantı sorunu: {e}")
                break 
                
        return []