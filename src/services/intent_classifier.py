import json
import os
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "intents", "intents.json")


with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


patterns = []
tags = []
responses = {}

for intent in data["intents"]:

    for pattern in intent["patterns"]:
        patterns.append(pattern.lower())
        tags.append(intent["tag"])

    responses[intent["tag"]] = intent["responses"]


# NLP Vectorizer
vectorizer = TfidfVectorizer()
pattern_vectors = vectorizer.fit_transform(patterns)


# ----------------------------
# INTENT PREDICTION
# ----------------------------
def predict_intent(user_message):

    user_message = user_message.lower()

    user_vector = vectorizer.transform([user_message])

    similarity = cosine_similarity(user_vector, pattern_vectors)

    best_match_index = similarity.argmax()

    score = similarity[0][best_match_index]

    # similarity threshold
    if score < 0.30:
        return "fallback"

    return tags[best_match_index]


# ----------------------------
# RESPONSE GENERATION
# ----------------------------
def get_ai_response(user_message):

    intent = predict_intent(user_message)

    if intent in responses:
        return random.choice(responses[intent])

    return "I'm not sure how to help with that."