import fitz  # PyMuPDF
from pathlib import Path

desktop_app = Path.home()/ "Desktop"
apps = [app for app in desktop_app.iterdir() if app.is_file()]

def search_file(file_name):

        desktop_app = Path.home()/ "Desktop"
        apps = [app for app in desktop_app.iterdir() if app.is_file()]

        for p in apps:
            if p.name.lower() == file_name.lower():
                full_path = p
                return p
        raise FileNotFoundError(f"No such file: {file_name} in desktop")

def load_pdf(file_name):

    path = search_file(file_name)
    doc = fitz.open(path)
    text= ""
    for page in doc:
        text += page.get_text()

    return text
    