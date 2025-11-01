import re
import os
import json
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# -----------------------------
# Helper: run OCR
# -----------------------------
def extract_text_from_file(file_path):
    text = ""
    file_ext = file_path.lower().split(".")[-1]

    if file_ext == "pdf":
        print("[INFO] Converting PDF pages to images...")
        pages = convert_from_path(file_path)
        for i, page in enumerate(pages):
            print(f"[INFO] Running OCR on page {i + 1}...")
            # --psm 6 treats text as a block, improves accuracy
            text += pytesseract.image_to_string(page, config="--psm 6")
    elif file_ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
        print("[INFO] Running OCR on image...")
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, config="--psm 6")
    else:
        raise ValueError("Unsupported file format. Use PDF or Image.")

    return text


# -----------------------------
# Helper: normalize OCR text
# -----------------------------
def clean_ocr_text(text):
    # Keep newlines for multiline regex matching
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


# -----------------------------
# Core: extract structured data
# -----------------------------
def extract_claim_fields(text):
    data = {}

    # Multiline-aware patterns
    patterns = {
        "claim_number": [
            r"Claim\s*(?:Number|No|ID)\s*[:\-]?\s*([\s\n\r]*)([A-Z0-9\-]+)"
        ],
        "customer_id": [
            r"(?:Customer|Client)\s*ID\s*[:\-]?\s*([\s\n\r]*)([A-Z0-9\-]+)"
        ],
        "claim_type": [
            r"Claim\s*Type\s*[:\-]?\s*([\s\n\r]*)([A-Za-z\s]+)"
        ],
        "claim_amount": [
            r"(?:Claim\s*Amount|Amount\s*Claimed|Total\s*Claim|Amount)\s*[:\-]?\s*([\s\n\r]*)(?:₹|\$)?\s*([\d,\.]+)"
        ],
        "nominee": [
            r"Nominee\s*[:\-]?\s*([\s\n\r]*)([A-Za-z\s]+)"
        ],
        "date": [
            r"(?:Date|Claim\s*Date|Incident\s*Date)\s*[:\-]?\s*([\s\n\r]*)(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            r"(?:Date|Claim\s*Date|Incident\s*Date)\s*[:\-]?\s*([\s\n\r]*)([0-9]{1,2}\s*[A-Za-z]{3,9}\s*[0-9]{4})"
        ],
        "bank_account_no": [
            r"(?:Account|A\/C|Bank\s*Account)\s*(?:Number|No)?\s*[:\-]?\s*([\s\n\r]*)(\d{6,20})"
        ],
        "name_of_claimant": [
            r"(?:Name\s*of\s*Claimant)\s*[:\-]?\s*([\s\n\r]*)([A-Za-z\s]+)"
        ]
    }

    for field, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(2).strip()
                value = re.sub(r"(Claim Amount|Nominee|Date|Bank|Account|No\.?)$", "", value, flags=re.IGNORECASE).strip()
                data[field] = value
                break

    # Fallback for missing fields
    if "claim_amount" not in data:
        amt = re.findall(r"(?:₹|\$)\s*\d[\d,\.]*", text)
        if amt:
            data["claim_amount"] = re.sub(r"[₹\$]", "", amt[0]).strip()

    if "date" not in data:
        date = re.findall(r"\b\d{1,2}[\/\-][A-Za-z0-9]{3,9}[\/\-]\d{2,4}\b", text)
        if date:
            data["date"] = date[0]

    return data


# -----------------------------
# Pipeline: file → text → JSON
# -----------------------------
def process_claim_document(file_path):
    print(f"\n[INFO] Processing file: {file_path}")
    text = extract_text_from_file(file_path)
    clean_text = clean_ocr_text(text)
    extracted_data = extract_claim_fields(clean_text)

    json_path = os.path.splitext(file_path)[0] + "_output.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)

    print(f"[SUCCESS] Extracted data saved to {json_path}")
    print(json.dumps(extracted_data, indent=4))
    return extracted_data


# -----------------------------
# Test run
# -----------------------------
if __name__ == "__main__":
    file_path = "METLIFE INSURANCE CLAIM FORM3.pdf"  # change as needed
    process_claim_document(file_path)
