from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import tempfile
from AI_analysis import process_claim_document  # <-- import your OCR code

app = FastAPI(title="Claim OCR API")

# Optional: allow frontend to call your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Claim OCR API is running"}

@app.post("/extract-claim")
async def extract_claim(file: UploadFile = File(...)):
    """Receive a file (PDF/image), run OCR, and return extracted fields."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        result = process_claim_document(temp_path)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        os.remove(temp_path)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
