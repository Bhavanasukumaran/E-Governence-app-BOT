from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import random
import os
from src.databases.database import init_db
from src.services.complaint_service import (
    get_complaint_status,
    register_complaint,
    predict_complaint_priority
)

from src.services.intent_classifier import predict_intent
from src.services.document_service import verify_document


app = FastAPI(title="E-Governance AI Chatbot")

init_db()

templates = Jinja2Templates(directory="templates")


# -----------------------------
# LOAD INTENTS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "src", "intents", "intents.json")

with open(INTENTS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)
    intents = data["intents"]


class ChatRequest(BaseModel):
    message: str


# -----------------------------
# CONVERSATION MEMORY
# -----------------------------
conversation_state = {}
complaint_data = {}


# -----------------------------
# INTENT RESPONSE HELPER
# -----------------------------
def get_intent_response(tag):

    for intent in intents:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])

    return "I'm not sure how to help with that."


# -----------------------------
# HOME PAGE
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -----------------------------
# CHAT API
# -----------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.lower()

    # -----------------------------
    # STEP HANDLING FIRST
    # -----------------------------

    # DOCUMENT VERIFICATION STEP
    if conversation_state.get("step") == "document_id":

        doc_id = request.message.strip().upper()

        result = verify_document(doc_id)

        conversation_state.clear()

        return {
            "bot_response": result
        }


    # COMPLAINT STATUS STEP
    if conversation_state.get("step") == "status_id":

        complaint_id = request.message.strip().upper()

        conversation_state.clear()

        status = get_complaint_status(complaint_id)

        return {
            "bot_response": f"Complaint Status\nID: {complaint_id}\nCurrent Status: {status}"
        }


    # COMPLAINT DESCRIPTION STEP
    if conversation_state.get("step") == "description":

        complaint_data["description"] = request.message
        conversation_state["step"] = "location"

        return {
            "bot_response": "Please enter the location of the issue."
        }


    # COMPLAINT LOCATION STEP
    if conversation_state.get("step") == "location":

        complaint_data["location"] = request.message

        description = complaint_data["description"]
        location = complaint_data["location"]

        complaint_id, priority = register_complaint(description, location)

        conversation_state.clear()
        complaint_data.clear()

        return {
            "bot_response": f"Complaint registered successfully.\nComplaint ID: {complaint_id}\nPriority Level: {priority}"
        }


    # -----------------------------
    # INTENT DETECTION AFTER STATE
    # -----------------------------
    intent = predict_intent(user_message)

    if intent is None:
        intent = "fallback"


    # -----------------------------
    # DOCUMENT VERIFICATION INTENT
    # -----------------------------
    if intent == "document_verification":

        conversation_state["step"] = "document_id"

        return {
            "bot_response": "Please provide your document reference ID."
        }


    # -----------------------------
    # COMPLAINT STATUS INTENT
    # -----------------------------
    if intent == "complaint_status":

        conversation_state["step"] = "status_id"

        return {
            "bot_response": "Please enter your complaint ID."
        }


    # -----------------------------
    # REGISTER COMPLAINT INTENT
    # -----------------------------
    if intent == "register_complaint":

        conversation_state["step"] = "description"

        return {
            "bot_response": "Please describe your complaint."
        }


    # -----------------------------
    # ISSUE PRIORITY DETECTION
    # -----------------------------
    issue_keywords = [
        "urgent",
        "delay",
        "not working",
        "problem",
        "issue",
        "fraud",
        "emergency",
        "critical"
    ]

    if any(word in user_message for word in issue_keywords):

        priority = predict_complaint_priority(user_message)

        return {
            "bot_response": f"This issue seems {priority} priority. You may register a complaint if required."
        }


    # -----------------------------
    # NORMAL CHAT RESPONSE
    # -----------------------------
    response_text = get_intent_response(intent)

    return {
        "user_message": request.message,
        "bot_response": response_text
    }