import os
import requests
import nltk
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from src.research_agent import ResearchAgent
from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import remove_references_section, clean_text, extract_abstract
from src.chunker import chunk_text
from src.similarity import SimilarityEngine
from src.text_summarizer import MultiModelSummarizer

console = Console()

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def download_pdf(pdf_url: str, save_path: str):

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(pdf_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if "text/html" in response.headers.get("Content-Type", ""):
            return False
            
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    console.clear()
    console.print(Panel.fit("[bold cyan]---ARAŞTIRMA ASİSTANI---[/bold cyan]", border_style="cyan"))

    konu = console.input("[bold yellow]Araştırma Konusu (Örn: Large Language Models in Healthcare): [/bold yellow]")
    odak_kelimesi = console.input("[bold yellow]Odak/Zorunlu Kelime (İstemiyorsanız boş bırakın): [/bold yellow]")
    
    agent = ResearchAgent()
    # ArXiv'den 15, Semantic Scholar'dan 15 = Toplam 30 makale toplanacak.
    uygun_makaleler = agent.search_and_score(query=konu, focus_word=odak_kelimesi, max_results=15, threshold=50.0)

    if not uygun_makaleler:
        console.print(Panel("[bold red]Uygun makale bulunamadı. Sistem kapatılıyor.[/bold red]"))
        exit()

    console.print("\n[bold magenta]Makaleler işleniyor[/bold magenta]")

    pdf_klasoru = "data/pdfs"
    os.makedirs(pdf_klasoru, exist_ok=True)

    basarili_islem = 0
    hedef_islem = 3

    for i, makale in enumerate(uygun_makaleler):
        if basarili_islem >= hedef_islem:
            break

        table = Table(show_header=False, box=None)
        table.add_row(f"\n[bold cyan]Sıradaki makale deneniyor (Liste Sırası: {i+1})[/bold cyan]")
        table.add_row(f"[bold white]Başlık:[/bold white] {makale['title']}")
        table.add_row(f"[bold white]Skor:[/bold white] [bold green]%{makale['similarity_score']:.1f}[/bold green] | [bold white]Kaynak:[/bold white] {makale.get('source', 'ArXiv')}")
        console.print(table)

        hedef_pdf_yolu = os.path.join(pdf_klasoru, f"temp_paper_{i}.pdf")
        indirme_linki = makale['pdf_url'] if makale['pdf_url'].endswith('.pdf') else makale['pdf_url'] + ".pdf"
        
        islem_basarili_mi = False

        with console.status(f"[bold blue]PDF erişimi test ediliyor ve okunuyor...[/bold blue]", spinner="dots"):
            if download_pdf(indirme_linki, hedef_pdf_yolu):
                try:
                    raw_text = extract_text_from_pdf(hedef_pdf_yolu)
                    
                    if len(raw_text.split()) < 50:
                        raise ValueError("PDF okunamayacak formatta")
                        
                    clean_txt = clean_text(remove_references_section(raw_text))
                    chunks = chunk_text(clean_txt, chunk_size=30, overlap=3)
                    
                    search_engine = SimilarityEngine()
                    abstract_text = extract_abstract(raw_text)
                    if len(abstract_text.split()) < 20: 
                        abstract_text = makale['abstract']
                        
                    top_chunks = search_engine.find_top_chunks(query=abstract_text, chunks=chunks, top_k=3)
                    focused_text = " ".join(top_chunks)
                    
                    app = MultiModelSummarizer()
                    final_summary = app.summarize(focused_text, method="abstractive_formal", min_length=150, max_length=250)
                    console.print(Panel(final_summary, title=f"[bold green]ÖZET[/bold green]", border_style="green", expand=False))
                    
                    islem_basarili_mi = True
                    
                except Exception as e:
                    console.print(f"[yellow]İçerik okunamadı! ({e}). Başka bir makale deneniyor...[/yellow]")
            else:
                console.print(f"[yellow]Makale linki doğrudan bir PDF içermiyor. Başka bir makale deneniyor...[/yellow]")

        if islem_basarili_mi:
            basarili_islem += 1

        if os.path.exists(hedef_pdf_yolu):
            os.remove(hedef_pdf_yolu)
            console.print(f"[dim]\\[TEMİZLİK] Geçici dosya silindi.[/dim]")

    if basarili_islem < hedef_islem:
        console.print(f"\n[bold yellow]Havuzdaki makaleler bittiği için yalnızca {basarili_islem} adet makale başarılı bir şekilde özetlenebildi.[/bold yellow]")

    console.print(Panel("[bold green]✅ TÜM İŞLEMLER TAMAMLANDI. SİSTEM TEMİZ DURUMDA.[/bold green]", expand=False))