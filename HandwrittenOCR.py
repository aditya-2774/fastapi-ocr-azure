import easyocr
import json
import cv2

def extract_handwritten_text(image_path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image_path)

    extracted_text = []
    for (bbox, text, confidence) in results:
        extracted_text.append({
            "text": text,
            "confidence": round(confidence, 2)
        })

    return extracted_text

if __name__ == "__main__":
    image_path = "HandwrittenClaim.jpg"
    data = extract_handwritten_text(image_path)

    with open("handwritten_ocr.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ Handwritten OCR complete! Output saved to handwritten_ocr.json")
