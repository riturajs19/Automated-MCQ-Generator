#!/bin/bash

# Update package list and install Tesseract OCR
apt-get update
apt-get install -y tesseract-ocr

# Create Streamlit config folder
mkdir -p ~/.streamlit/

# Set Streamlit server configuration
echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
