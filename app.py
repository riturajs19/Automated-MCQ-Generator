import streamlit as st


st.set_page_config(page_title="📘 Interactive MCQ Quiz", layout="centered")


import random
import pytesseract
import platform
import numpy as np
import cv2
import spacy
from PIL import Image
import PyPDF2
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
import shutil
import unicodedata


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ✅ Tesseract path setup
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

if shutil.which("tesseract") is None:
    st.error("❌ Tesseract is not installed or not found in PATH.")
    st.stop()

# ================= Utility Functions =================

def preprocess_image(img):
    img = img.convert("L")
    open_cv_image = np.array(img)
    _, thresh_img = cv2.threshold(open_cv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh_img)

def sanitize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def extract_nouns(text):
    doc = nlp(text)
    return list(set(token.text for token in doc if token.pos_ == "NOUN" and len(token.text) > 2))

def generate_mcqs_from_text(text, num_questions=5):
    doc = nlp(text)
    sentences = list(doc.sents)
    all_nouns = extract_nouns(text)
    mcqs = []
    used_sentences = set()

    for sent in sentences:
        if len(mcqs) >= num_questions:
            break
        noun_tokens = [token for token in sent if token.pos_ == "NOUN" and len(token.text) > 2]
        if not noun_tokens:
            continue
        correct = random.choice(noun_tokens).text
        sentence = sent.text.strip()
        if sentence in used_sentences or correct not in sentence:
            continue
        used_sentences.add(sentence)
        blanked = sentence.replace(correct, "____", 1)
        distractors = [n for n in all_nouns if n != correct]
        if len(distractors) < 3:
            continue
        options = random.sample(distractors, 3) + [correct]
        random.shuffle(options)
        mcqs.append({"question": blanked, "options": options, "answer": correct})
    return mcqs

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
            pdf.cell(0, 10, f"   - {sanitize_text(opt)}", ln=True)
        pdf.cell(0, 10, f"Answer: {sanitize_text(q['answer'])}", ln=True)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin1')

def get_pdf_download_link(pdf_data):
    b64 = base64.b64encode(pdf_data).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="mcq_quiz.pdf">📥 Download MCQs as PDF</a>'

# ================= Streamlit App =================

st.title("🧠 MCQ Generator from Screenshot, PDF or Manual Text")

quotes = [
    "Believe in yourself and all that you are! 🌟",
    "Your only limit is your mind. 💡",
    "Every expert was once a beginner. 🚀",
    "Success is the sum of small efforts. 🔁",
    "Don’t wish for it. Work for it. 🎯"
]

uploaded_file = st.file_uploader("📤 Upload a PDF or Image (screenshot) to extract text", type=["pdf", "png", "jpg", "jpeg"])
text = ""

if uploaded_file:
    file_type = uploaded_file.type
    if "pdf" in file_type:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        st.success("✅ PDF uploaded and text extracted.")
    elif "image" in file_type:
        img = Image.open(uploaded_file)
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang='eng')
        st.success("✅ Image processed using OCR.")

# ✍️ Manual editable area
text = st.text_area("✏️ Edit or write paragraph (used for MCQ generation)", value=text, height=250)
text = sanitize_text(text.strip())

# 🎯 Number of questions
num_questions = st.slider("🎯 Select number of MCQs to generate", 1, 20, 5)

# Generate Quiz
if st.button("🚀 Generate Quiz"):
    if not text:
        st.warning("⚠️ Please enter or upload some text.")
    else:
        with st.spinner("Generating MCQs..."):
            mcqs = generate_mcqs_from_text(text, num_questions)
            if not mcqs:
                st.error("❌ Could not generate any MCQs.")
            else:
                st.session_state["mcqs"] = mcqs
                st.session_state["submitted"] = False
                st.rerun()

# Quiz Form
if "mcqs" in st.session_state and not st.session_state.get("submitted", False):
    with st.form("quiz_form"):
        st.subheader("📚 Your Quiz")
        user_answers = []
        for idx, q in enumerate(st.session_state["mcqs"]):
            st.markdown(f"**Q{idx + 1}. {q['question']}**")
            user_choice = st.radio("", q['options'], key=f"q_{idx}")
            user_answers.append(user_choice)
        submitted = st.form_submit_button("✅ Submit Answers")
        if submitted:
            st.session_state["submitted"] = True
            st.session_state["user_answers"] = user_answers
            st.rerun()

# Results
if st.session_state.get("submitted", False):
    correct = 0
    wrong = 0
    st.subheader("📊 Results")

    for idx, q in enumerate(st.session_state["mcqs"]):
        user = st.session_state["user_answers"][idx]
        ans = q["answer"]
        st.markdown(f"**Q{idx + 1}: {q['question']}**")
        for opt in q["options"]:
            if opt == ans:
                st.markdown(f"- ✅ **{opt}**", unsafe_allow_html=True)
            elif opt == user:
                st.markdown(f"- ❌ *{opt}*", unsafe_allow_html=True)
            else:
                st.markdown(f"- {opt}")
        if user == ans:
            st.success("Correct!")
            correct += 1
        else:
            st.error(f"Wrong — You selected `{user}`, correct is `{ans}`")
        st.markdown("---")

    st.info(f"🎯 Score: **{correct}/{len(st.session_state['mcqs'])}**")
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie([correct, len(st.session_state['mcqs']) - correct],
           labels=["Correct", "Wrong"], colors=["green", "red"], autopct="%1.1f%%")
    st.pyplot(fig)

    pdf_bytes = generate_pdf(st.session_state["mcqs"])
    st.markdown(get_pdf_download_link(pdf_bytes), unsafe_allow_html=True)

    st.markdown(f"💡 {random.choice(quotes)}")

    if st.button("🔁 Start Over"):
        st.session_state.clear()
        st.rerun()
