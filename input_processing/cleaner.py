import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)   # remove extra spaces
    text = text.strip()
    return text
