from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.routes.upload import router as upload_router

app = FastAPI(title="Autobody Estimate Parser API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple HTML form for manual PDF upload
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

# Mount the upload route
app.include_router(upload_router)