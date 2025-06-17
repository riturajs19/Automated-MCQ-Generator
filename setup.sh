#!/bin/bash

apt-get update
apt-get install -y tesseract-ocr

mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml
