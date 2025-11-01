#!/bin/bash
echo "🔧 Installing poppler-utils and tesseract..."
apt-get update && apt-get install -y poppler-utils tesseract-ocr
echo "✅ Poppler and Tesseract installed"

# Start FastAPI app with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
