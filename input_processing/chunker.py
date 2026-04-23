import re

def chunk_text(text: str, max_words: int = 300) -> list[str]:
    # Split on sentence boundaries to avoid cutting mid-sentence
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_words = []
    current_count = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        if current_count + word_count > max_words and current_words:
            chunks.append(" ".join(current_words))
            current_words = []
            current_count = 0
        current_words.append(sentence)
        current_count += word_count

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks if chunks else [text]
