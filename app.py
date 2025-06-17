import pytesseract
from PIL import Image
import streamlit as st
import PyPDF2
import numpy as np
import cv2
import random
from MCQ_Generator import generate_mcqs_from_text

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Streamlit setup
st.set_page_config(page_title="📘 Interactive MCQ Quiz", layout="centered")
st.title("🧠 Interactive MCQ Quiz from PDF or Image")

# Image preprocessing
def preprocess_image(img):
    img = img.convert("L")
    open_cv_image = np.array(img)
    _, thresh_img = cv2.threshold(open_cv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh_img)

# File uploader
uploaded_file = st.file_uploader("Upload a PDF or Image (JPEG/PNG)", type=["pdf", "jpg", "jpeg", "png"])

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

# Number of questions
num_questions = st.slider("Select number of MCQs to generate", 1, 10, 5)

# Generate Quiz
if st.button("Generate Quiz"):
    if not text.strip():
        st.warning("Please upload a valid file with readable text.")
    else:
        with st.spinner("Generating MCQs..."):
            mcqs = generate_mcqs_from_text(text, num_questions)
            if not mcqs:
                st.error("❌ Could not generate any questions.")
            else:
                st.session_state["mcqs"] = mcqs
                st.session_state["submitted"] = False
                st.rerun()

# Show MCQs
if "mcqs" in st.session_state and not st.session_state.get("submitted", False):
    with st.form("quiz_form"):
        st.subheader("📝 Quiz")
        user_answers = []
        for idx, q in enumerate(st.session_state["mcqs"]):
            st.markdown(f"<h5 style='font-size: 20px;'>Q{idx + 1}. {q['question']}</h5>", unsafe_allow_html=True)
            user_choice = st.radio("", q['options'], key=f"q_{idx}")
            user_answers.append(user_choice)

        submitted = st.form_submit_button("Submit Answers")
        if submitted:
            st.session_state["submitted"] = True
            st.session_state["user_answers"] = user_answers
            st.rerun()

# Show Results
if st.session_state.get("submitted", False):
    st.subheader("📊 Results")
    correct_count = 0

    for idx, q in enumerate(st.session_state["mcqs"]):
        user_ans = st.session_state["user_answers"][idx]
        correct_ans = q["answer"]
        if user_ans == correct_ans:
            st.success(f"✅ Q{idx + 1}: Correct! `{correct_ans}`")
            correct_count += 1
        else:
            st.error(f"❌ Q{idx + 1}: Wrong — You chose `{user_ans}`, Correct is `{correct_ans}`")
        st.markdown("---")

    st.info(f"🎯 Your Score: **{correct_count} / {len(st.session_state['mcqs'])}**")
    st.balloons()
# Reset button  