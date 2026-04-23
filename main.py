from core.workflow_engine import run_workflow
from input_processing.text_handler import read_text_file
from input_processing.pdf_handler import read_pdf
from input_processing.cleaner import clean_text
from ui.main_window import run_app

def process_file(file_path: str):
    if file_path.endswith(".txt"):
        text = read_text_file(file_path)

    elif file_path.endswith(".pdf"):
        text = read_pdf(file_path)

    else:
        raise ValueError("Unsupported file type")

    cleaned = clean_text(text)

    return run_workflow(cleaned, workflow="tasks")


if __name__ == "__main__":
    run_app()