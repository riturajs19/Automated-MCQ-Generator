import random
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_nouns(text):
    doc = nlp(text)
    return list(set(token.text for token in doc if token.pos_ == "NOUN" and len(token.text) > 2))

def generate_mcqs_from_text(text, num_questions=3):
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

        mcqs.append({
            "question": blanked,
            "options": options,
            "answer": correct
        })

    return mcqs

# ---- RUN THE MCQ GENERATOR ----
text = """
Statistics is the science of collecting, organizing, and interpreting data.
Probability is a measure of the likelihood that a particular event will occur.
It is used in fields such as mathematics, finance, and artificial intelligence.
"""

mcqs = generate_mcqs_from_text(text, 3)

# ✅ Clean Output
for i, mcq in enumerate(mcqs, 1):
    print(f"\nQ{i}. {mcq['question']}")
    for j, opt in enumerate(mcq['options']):
        print(f"   {chr(65 + j)}. {opt}")
    print(f"✅ Answer: {mcq['answer']}")
