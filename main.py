from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import re
import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# TEMP: allow all origins (for debugging)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # <-- allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app = FastAPI(title="Smart Claim Analyzer", version="0.1.0")

# -----------------------------
# Helper: extract text from PDF / Image
# -----------------------------
def extract_text_from_file(file_path: str) -> str:
    text = ""
    ext = file_path.lower().split(".")[-1]
    if ext == "pdf":
        pages = convert_from_path(file_path)
        for page in pages:
            text += pytesseract.image_to_string(page, config="--psm 6")
    elif ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, config="--psm 6")
    else:
        raise ValueError("Unsupported file format. Use PDF or image.")
    return text


# -----------------------------
# Helper: clean text
# -----------------------------
def clean_text(text: str) -> str:
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# -----------------------------
# Helper: extract structured fields
# -----------------------------
def extract_claim_fields(text: str) -> dict:
    data = {}

    patterns = {
        "claim_number": [
            r"Claim\s*(?:Number|No|ID)\s*[:\-]?\s*([A-Z0-9\-]+)",
            r"Claim\s*#\s*([A-Z0-9\-]+)"
        ],
        "customer_id": [r"(?:Customer|Client)\s*ID\s*[:\-]?\s*(\d+)"],
        "claim_type": [
            r"Claim\s*Type\s*[:\-]?\s*([A-Za-z\s]+?)(?=\s*(?:Claim\s*Amount|Nominee|Date|Bank|$))"
        ],
        "claim_amount": [
            r"(?:Claim\s*Amount|Amount\s*Claimed|Total\s*Claim)\s*[:\-]?\s*(?:\$|₹)?\s*([\d,\.]+)"
        ],
        "nominee": [
            r"Nominee\s*[:\-]?\s*([A-Za-z\s]+?)(?=\s*(?:Date|Bank|Account|$))"
        ],
        "date": [
            r"(?:Date|Claim\s*Date|Incident\s*Date)\s*[:\-]?\s*([0-9]{1,2}\s*[A-Za-z]{3,9}\s*[0-9]{4})",
            r"(?:Date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
        ],
        "bank_account_no": [
            r"(?:Account|A\/C|Bank\s*Account)\s*(?:Number|No)?\s*[:\-]?\s*(\d{6,20})"
        ]
    }

    for field, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = re.sub(
                    r"(Claim Amount|Nominee|Date|Bank|Account|No\.?)$",
                    "",
                    match.group(1).strip(),
                    flags=re.IGNORECASE,
                ).strip()
                data[field] = value
                break

    # fallback for amount and date
    if "claim_amount" not in data:
        amt = re.findall(r"(?:₹|\$)\s*\d[\d,\.]*", text)
        if amt:
            data["claim_amount"] = amt[0]

    if "date" not in data:
        date = re.findall(r"\b\d{1,2}[\/\-][A-Za-z0-9]{3,9}[\/\-]\d{2,4}\b", text)
        if date:
            data["date"] = date[0]

    return data


# -----------------------------
# API Endpoint: /extract-claim
# -----------------------------
@app.post("/extract-claim", summary="Extract claim info from a PDF or image")
async def extract_claim(file: UploadFile = File(...)):
    try:
        # Save to temp file
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # OCR + Extraction
        text = extract_text_from_file(tmp_path)
        text = clean_text(text)
        result = extract_claim_fields(text)

        # Cleanup temp file
        os.remove(tmp_path)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
