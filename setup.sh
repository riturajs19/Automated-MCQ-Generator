#!/bin/bash

# Install tesseract OCR
apt-get update && apt-get install -y tesseract-ocr

# Optional: Install English language (usually default)
apt-get install -y tesseract-ocr-eng

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .streamlit config for Streamlit deployment
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml
