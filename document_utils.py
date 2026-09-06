from pypdf import PdfReader
from docx import Document

def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

def extract_docx_text(uploaded_file):
    try:
        document = Document(uploaded_file)

        paragraphs = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        if not paragraphs:
            return None

        return "\n".join(paragraphs)

    except Exception:
        return None