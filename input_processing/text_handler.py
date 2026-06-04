def read_text_file(file_path: str) -> str:
    with open(file_path, encoding="utf-8") as f:
        return f.read()
