import os

def read_file(path: str, encoding: str = "utf-8") -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding=encoding) as f:
        return f.read()

def get_extension(path: str) -> str:
    return os.path.splitext(path)[1].lower()

def is_supported(path: str) -> bool:
    return get_extension(path) in {".txt", ".pdf"}
