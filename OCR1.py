import pytesseract
from pdf2image import convert_from_path
import json
import os

# Optional: specify tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    text_data = []
    for i, page in enumerate(pages):
        print(f"🧾 Processing page {i+1}...")
        text = pytesseract.image_to_string(page)
        text_data.append({
            "page_number": i + 1,
            "text": text.strip()
        })
    return text_data

if __name__ == "__main__":
    pdf_path = "METLIFE INSURANCE CLAIM FORM.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
    else:
        data = extract_text_from_pdf(pdf_path)
        print("\n✅ OCR Extraction Complete!\n")

        # Save as text file
        with open("output.txt", "w", encoding="utf-8") as f:
            for page in data:
                f.write(f"\n--- Page {page['page_number']} ---\n")
                f.write(page["text"] + "\n")

        # Save as JSON
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("📁 Extracted text saved as:")
        print(" - output.txt (plain text)")
        print(" - output.json (structured JSON)")
