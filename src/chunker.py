
#Metni cümlelere ayırıp, belirtilen boyutlarda parçalara böler.

import nltk

# NLTK punkt verisini indir
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def split_sentences(text: str) -> list:
    """
    Metni cümlelere ayırır. NLTK'nın sent_tokenize'ını kullanır.
    """
    # Boş metin kontrolü
    if not text or not isinstance(text, str):
        return []
    
    # NLTK ile cümlelere ayır
    sentences = nltk.sent_tokenize(text)
    
    # Cümleleri temizle baş ve sondaki boşlukları al, boş olanları çıkar
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def chunk_by_sentences(sentences: list, chunk_size: int = 10, overlap: int = 2) -> list:
    
    #Cümle listesini belirtilen büyüklükte ve örtüşme oranında parçalara ayırır.
        #sentences: Cümle listesi.
        #chunk_size Her bir parçadaki cümle sayısı.
        #overlap: Ardışık parçalar arasında örtüşen cümle sayısı.
        #list: Her biri birleştirilmiş cümle metni olan parçalar listesi.

    if not sentences:
        return []
    
    chunks = []
    step = chunk_size - overlap
    if step <= 0:
        step = 1  # overlap >= chunk_size ise sonsuz döngüye girme
    
    i = 0
    while i < len(sentences):
        # chunk için cümleleri al
        end = min(i + chunk_size, len(sentences))
        chunk_sentences = sentences[i:end]
        chunk_text = ' '.join(chunk_sentences)
        chunks.append(chunk_text)
        
        # Bir sonraki chunk'ın başlangıcı
        i += step
    
    # Son chunk'ın çok kısa olması durumunda bir öncekiyle birleştir
    if len(chunks) > 1 and len(split_sentences(chunks[-1])) < overlap:
        # son parçayı sondan bir öncekiyle birleştir
        chunks[-2] = chunks[-2] + " " + chunks[-1]
        chunks.pop()
    
    return chunks


def chunk_text(text: str, chunk_size: int = 10, overlap: int = 2) -> list:

    #Verilen metni cümlelere ayırıp parçalara böler.
        #text: Temizlenmiş metin.
        #chunk_size: Parça başına cümle sayısı.
        #overlap: Örtüşen cümle sayısı.
        #list: Parçalanmış metin listesi.

    sentences = split_sentences(text)
    if not sentences:
        return []
    return chunk_by_sentences(sentences, chunk_size, overlap)


""" def chunk_with_word_limit(text: str, word_limit: int = 500, overlap_words: int = 50) -> list:
    
    Kelime sayısına göre parçalama (alternatif yöntem).
    Bu daha esnek ama cümle bütünlüğü bozulabilir.
    Kullanmayacağım ama referans olarak ekledim.
    
    # boşluklara göre ayır
    words = text.split()
    if not words:
        return []
    
    chunks = []
    i = 0
    while i < len(words):
        end = min(i + word_limit, len(words))
        chunk_words = words[i:end]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        i += word_limit - overlap_words
    return chunks """


if __name__ == "__main__":
    # Test
    test_text = """
    Bu birinci cümle. Bu ikinci cümle. Bu üçüncü cümle.
    Dördüncü cümle biraz daha uzun olabilir. Beşinci cümle.
    Altıncı cümle. Yedinci cümle. Sekizinci cümle.
    Dokuzuncu cümle. Onuncu cümle. On birinci cümle.
    On ikinci cümle. On üçüncü cümle. On dördüncü cümle.
    On beşinci cümle. On altıncı cümle. On yedinci cümle.
    """
    
    print("Cümlelere ayırma:")
    sentences = split_sentences(test_text)
    for i, s in enumerate(sentences):
        print(f"{i+1}: {s}")
    
    print("\nParçalama (chunk_size=5, overlap=2):")
    chunks = chunk_text(test_text, chunk_size=5, overlap=2)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {chunk}")
        print(f"Karakter sayısı: {len(chunk)}")
        print()