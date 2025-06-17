import pytesseract
from PIL import Image
import streamlit as st
import PyPDF2
import numpy as np
import cv2
import random
import platform
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
from MCQ_Generator import generate_mcqs_from_text
import os
import shutil
import unicodedata

# ✅ Streamlit config (must be first)
st.set_page_config(page_title="📘 Interactive MCQ Quiz", layout="centered")
st.title("🧠 Interactive MCQ Quiz from PDF or Image")

# ✅ Tesseract path (for Windows/Linux)
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ✅ Check if Tesseract is in path
if shutil.which("tesseract") is None:
    st.error("❌ Tesseract is not installed or not found in PATH.")
    st.stop()

# ✅ Clean non-ASCII for PDF output
def sanitize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

# ✅ Preprocess images for OCR
def preprocess_image(img):
    img = img.convert("L")
    open_cv_image = np.array(img)
    _, thresh_img = cv2.threshold(open_cv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh_img)

# ✅ Generate PDF from MCQs
def generate_pdf(mcqs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="MCQ Quiz", ln=True, align='C')
    pdf.ln(5)
    for idx, q in enumerate(mcqs):
        question = sanitize_text(q['question'])
        pdf.multi_cell(0, 10, f"Q{idx+1}. {question}")
        for opt in q['options']:
            option = sanitize_text(opt)
            pdf.cell(0, 10, f"   - {option}", ln=True)
        answer = sanitize_text(q['answer'])
        pdf.cell(0, 10, f"Answer: {answer}", ln=True)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin1')

# ✅ Create PDF download link
def get_pdf_download_link(pdf_data):
    b64 = base64.b64encode(pdf_data).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="mcq_quiz.pdf">📥 Download MCQs as PDF</a>'

# ✅ Motivational quotes
quotes = [
    "Believe in yourself and all that you are! 🌟",
    "Your only limit is your mind. 💡",
    "Every expert was once a beginner. 🚀",
    "Success is the sum of small efforts. 🔁",
    "Don’t wish for it. Work for it. 🎯"
]

# ✅ File upload
uploaded_file = st.file_uploader("📤 Upload a PDF or Image (JPEG/PNG)", type=["pdf", "jpg", "jpeg", "png"])
text = ""

if uploaded_file is not None:
    file_type = uploaded_file.type

    if "pdf" in file_type:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        st.success("✅ PDF uploaded successfully")

    elif "image" in file_type:
        img = Image.open(uploaded_file)
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang='eng')
        st.success("✅ Image processed with OCR")

    st.text_area("📝 Extracted Text", text, height=200)

# ✅ Question slider
num_questions = st.slider("🎯 Select number of MCQs to generate", 1, 20, 5)

# ✅ Generate Quiz
if st.button("Generate Quiz"):
    if not text.strip():
        st.warning("⚠️ Please upload a valid file with readable text.")
    else:
        with st.spinner("⏳ Generating MCQs..."):
            mcqs = generate_mcqs_from_text(text, num_questions)
            if not mcqs:
                st.error("❌ Could not generate any questions.")
            else:
                st.session_state["mcqs"] = mcqs
                st.session_state["submitted"] = False
                st.rerun()

# ✅ Show MCQs form
if "mcqs" in st.session_state and not st.session_state.get("submitted", False):
    with st.form("quiz_form"):
        st.subheader("📚 Quiz Time")
        user_answers = []
        for idx, q in enumerate(st.session_state["mcqs"]):
            st.markdown(f"<h5 style='font-size: 20px;'>Q{idx + 1}. {q['question']}</h5>", unsafe_allow_html=True)
            user_choice = st.radio("", q['options'], key=f"q_{idx}")
            user_answers.append(user_choice)

        submitted = st.form_submit_button("✅ Submit Answers")
        if submitted:
            st.session_state["submitted"] = True
            st.session_state["user_answers"] = user_answers
            st.rerun()

# ✅ Show results
if st.session_state.get("submitted", False):
    st.subheader("📊 Results")
    correct_count = 0
    wrong_count = 0

    for idx, q in enumerate(st.session_state["mcqs"]):
        user_ans = st.session_state["user_answers"][idx]
        correct_ans = q["answer"]

        st.markdown(f"**Q{idx + 1}: {q['question']}**")

        for opt in q['options']:
            if opt == correct_ans:
                st.markdown(f"- ✅ <span style='color:green;font-weight:bold'>{opt}</span>", unsafe_allow_html=True)
            elif opt == user_ans:
                st.markdown(f"- ❌ <span style='color:red;font-weight:bold'>{opt}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"- {opt}")

        if user_ans == correct_ans:
            st.success("Correct!")
            correct_count += 1
        else:
            st.error(f"Wrong — You chose `{user_ans}`, Correct is `{correct_ans}`")
            wrong_count += 1

        st.markdown("---")

    # ✅ Show score + chart
    st.info(f"🎯 Your Score: **{correct_count} / {len(st.session_state['mcqs'])}**")
    fig, ax = plt.subplots(figsize = (3,3))
ax.pie([correct_count, wrong_count], labels=['Correct', 'Wrong'], autopct='%1.1f%%', colors=["green", "red"])
    st.pyplot(fig)

    # ✅ PDF download
    pdf_bytes = generate_pdf(st.session_state["mcqs"])
    st.markdown(get_pdf_download_link(pdf_bytes), unsafe_allow_html=True)

    # ✅ Motivation
    st.markdown(f"💡 **{random.choice(quotes)}**")

    # ✅ Restart
    if st.button("🔄 Start Over"):
        st.session_state.clear()
        st.rerun()
