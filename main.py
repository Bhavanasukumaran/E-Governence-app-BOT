from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
import json
import random
import os

app = FastAPI(title="E-Governance AI Chatbot")
templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "src", "intents", "intents.json")

with open(INTENTS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)
    intents = data["intents"]

class ChatRequest(BaseModel):
    message: str


def find_response(user_message: str):
    user_message = user_message.lower()

    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_message:
                return random.choice(intent["responses"])

    return "Sorry, I didn't understand that. Please rephrase your question."

def predict_complaint_priority(text: str):
    text = text.lower()

    high_keywords = ["urgent", "immediately", "emergency", "fraud", "danger", "critical"]
    medium_keywords = ["delay", "not working", "issue", "problem", "slow"]
    
    for word in high_keywords:
        if word in text:
            return "High"

    for word in medium_keywords:
        if word in text:
            return "Medium"

    return "Low"


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message.lower()

    # Always check for complaint-type keywords
    issue_keywords = ["urgent", "delay", "not working", "problem", "issue", "fraud", "emergency", "critical"]

    if any(word in user_message for word in issue_keywords):
        priority = predict_complaint_priority(user_message)

        return {
            "user_message": request.message,
            "bot_response": f"Your complaint has been registered and marked as {priority} priority.",
            "predicted_priority": priority
        }

    # Otherwise normal intent matching
    response = find_response(request.message)

    return {
        "user_message": request.message,
        "bot_response": response
    }