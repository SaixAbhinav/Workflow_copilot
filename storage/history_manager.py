from storage.database import clear_history, get_history, save_result


def record(workflow: str, input_text: str, result: dict):
    save_result(workflow, input_text, result)

def fetch(limit: int = 50) -> list[dict]:
    return get_history(limit)

def purge():
    clear_history()
