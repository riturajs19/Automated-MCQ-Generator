import random
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")



def extract_nouns(text):
    doc = nlp(text)
    return list(set([token.text for token in doc if token.pos_ == "NOUN" and len(token.text) > 2]))

def generate_mcqs_from_text(text, num_questions):
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
        sentence_text = sent.text.strip()

        if correct not in sentence_text or sentence_text in used_sentences:
            continue

        # Replace only first occurrence of correct answer with blank
        blanked_sentence = sentence_text.replace(correct, "____", 1)
        used_sentences.add(sentence_text)

        # Generate options
        distractors = random.sample([n for n in all_nouns if n != correct], k=3) if len(all_nouns) >= 4 else []
        options = distractors + [correct]
        random.shuffle(options)

        mcqs.append({
            "question": blanked_sentence,
            "options": options,
            "answer": correct
        })

    return mcqs
