from document_utils import extract_docx_text

with open("word_test.docx", "rb") as file:
    text = extract_docx_text(file)

print(text)