import re
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
import html

from app.services.parser import scan_repair_lines
from app.services.pdf_reader import extract_text_from_pdf

app = FastAPI()
upload_router = APIRouter()

# Enable CORS for Wix or other frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Wix domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML form for manual PDF upload
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head><title>Upload Estimate</title></head>
        <body>
            <h2>Upload Estimate PDF</h2>
            <form action="/upload/" enctype="multipart/form-data" method="post">
                <input name="file" type="file" />
                <input type="submit" value="Upload" />
            </form>
        </body>
    </html>
    """

# Upload route with clean output formatting
@upload_router.post("/upload/", response_class=HTMLResponse)
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    lines = text.splitlines()
    repair_lines = scan_repair_lines(lines)
    formatted_lines = []
    for line in repair_lines:
        parts = line.split()
        op_parts = []
        time_parts = []
        for part in parts:
            if re.fullmatch(r"\d\.\d", part):  # Only match time values like 5.0, 3.3
            
                time_parts.append(part)
            else:
                op_parts.append(part)
        op_text = " ".join(op_parts)
        time_text = " ".join(f"{t:>5}" for t in time_parts)
          # Right-align each time value
        formatted_lines.append(f"{op_text:<50}{time_text}")

    raw_output = "\n".join(formatted_lines)
    escaped_output = html.escape(raw_output)

    return f"""
    <html>
        <head><title>Estimate Results</title></head>
        <body>
            <h2>Repair Lines from Estimate</h2>
            <pre>{escaped_output}</pre>
            <br><a href="/">Upload Another</a>
        </body>
    </html>
    """

# Mount the upload route
app.include_router(upload_router)