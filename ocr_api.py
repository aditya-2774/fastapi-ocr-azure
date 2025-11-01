from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import tempfile
from AI_analysis1 import process_claim_document  # Import your OCR logic

app = FastAPI()

@app.post("/extract-claim")
async def extract_claim(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        extracted_data = process_claim_document(tmp_path)
        return JSONResponse(content=extracted_data)
    finally:
        os.remove(tmp_path)
