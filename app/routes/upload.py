import io
import pdfplumber
from fastapi import APIRouter, UploadFile, File
from app.services.parser import parse_pdf_lines

router = APIRouter()

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    lines = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.splitlines())

    parsed_items = parse_pdf_lines(lines)
    return {"items": parsed_items}