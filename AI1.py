import json
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_document(text):
    # Break into lines for structure understanding
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Analyze structure: find key-value pairs
    key_value_pairs = {}
    for line in lines:
        if ":" in line:
            key, value = map(str.strip, line.split(":", 1))
            key_value_pairs[key] = value

    # Use NLP for semantic understanding
    doc = nlp(text)
    persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    moneys = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]

    semantic_info = {
        "Persons": persons,
        "Organizations": orgs,
        "Dates": dates,
        "Amounts": moneys,
    }

    # Merge structured + semantic data
    return {
        "KeyValuePairs": key_value_pairs,
        "SemanticEntities": semantic_info
    }


if __name__ == "__main__":
    with open("output.json", "r", encoding="utf-8") as f:
        pages = json.load(f)
    combined_text = " ".join([p["text"] for p in pages])

    analysis_result = analyze_document(combined_text)

    with open("document_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=4, ensure_ascii=False)

    print("\n✅ Document AI Analysis Complete! Saved as document_analysis.json")
    print(json.dumps(analysis_result, indent=4))
