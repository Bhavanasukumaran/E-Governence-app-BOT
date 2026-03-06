from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
import json
import random
import os
import uuid
from src.databases.database import init_db

app = FastAPI(title="E-Governance AI Chatbot")

init_db()

templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "src", "intents", "intents.json")

with open(INTENTS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)
    intents = data["intents"]


class ChatRequest(BaseModel):
    message: str


# Conversation state
conversation_state = {}
complaint_data = {}


def find_response(user_message: str):
    user_message = user_message.lower()

    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_message:
                return random.choice(intent["responses"])

    return "Sorry, I didn't understand that. Please rephrase your question."


def predict_complaint_priority(text: str):

    text = text.lower()

    high_keywords = [
        "urgent", "immediately", "emergency",
        "fraud", "danger", "critical"
    ]

    medium_keywords = [
        "delay", "not working", "issue",
        "problem", "slow"
    ]

    for word in high_keywords:
        if word in text:
            return "High"

    for word in medium_keywords:
        if word in text:
            return "Medium"

    return "Low"


def generate_complaint_id():
    return "GOV-" + str(uuid.uuid4())[:6].upper()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.lower()

    # CHECK COMPLAINT STATUS
    if "status" in user_message:
        return {
            "bot_response": "Please enter your complaint ID to check status."
        }

    # START COMPLAINT REGISTRATION
    if "file complaint" in user_message or "register complaint" in user_message:
        conversation_state["step"] = "description"

        return {
            "bot_response": "Please describe your complaint."
        }

    # STEP 2 : Get complaint description
    if conversation_state.get("step") == "description":

        complaint_data["description"] = request.message
        conversation_state["step"] = "location"

        return {
            "bot_response": "Please enter the location of the issue."
        }

    # STEP 3 : Get location
    if conversation_state.get("step") == "location":

        complaint_data["location"] = request.message

        description = complaint_data["description"]
        priority = predict_complaint_priority(description)
        complaint_id = generate_complaint_id()

        conversation_state.clear()
        complaint_data.clear()

        return {
            "bot_response": f"Complaint registered successfully.\nComplaint ID: {complaint_id}\nPriority Level: {priority}"
        }

    # Existing complaint keyword detection
    issue_keywords = [
        "urgent", "delay", "not working",
        "problem", "issue", "fraud",
        "emergency", "critical"
    ]

    if any(word in user_message for word in issue_keywords):

        priority = predict_complaint_priority(user_message)

        return {
            "user_message": request.message,
            "bot_response": f"Your complaint has been registered and marked as {priority} priority.",
            "predicted_priority": priority
        }

    # Normal chatbot response
    response = find_response(request.message)

    return {
        "user_message": request.message,
        "bot_response": response
    }