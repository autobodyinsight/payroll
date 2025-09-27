import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text()
        text += page_text
    print("Extracted PDF text:\n", text)  # Debug output
    return text