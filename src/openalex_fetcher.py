import requests

class OpenAlexFetcher:
    def __init__(self):
        self.base_url = "https://api.openalex.org/works"

    def search_papers(self, query: str, max_results: int = 15):
        print(f"\n OpenAlex'te '{query}' aranıyor...")
        
        params = {
            "search": query,
            "filter": "has_pdf_url:true", 
            "per-page": 50,
            "mailto": "aysekaya@gmail.com" 
        }
        papers = []
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data.get("results", []):
                best_oa = item.get("best_oa_location") or {}
                pdf_url = best_oa.get("pdf_url")
                
                
                abstract_inverted = item.get("abstract_inverted_index")

                if pdf_url and pdf_url.endswith('.pdf') and abstract_inverted:
                    
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
                        "source": "OpenAlex"
                    })

                    if len(papers) >= max_results:
                        break
                        
            print(f" -> Başarılı: OpenAlex'ten {len(papers)} adet pdf çekildi.")
            return papers

        except Exception as e:
            print(f"[HATA] OpenAlex bağlantı sorunu: {e}")
            return []