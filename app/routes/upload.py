from fastapi import APIRouter, UploadFile, File
from app.services.parser import parse_pdf_lines
from app.services.pdf_reader import extract_text_from_pdf

router = APIRouter()

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    lines = text.splitlines()
    parsed_items = parse_pdf_lines(lines)
    return {"items": parsed_items}