from fastapi import APIRouter, UploadFile, File
from app.services.pdf_reader import extract_text_from_pdf
from app.services.parser import parse_estimate
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text_from_pdf(content)
    parsed_items = parse_estimate(text)
    return JSONResponse(content={"items": parsed_items})