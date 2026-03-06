import uuid
from datetime import datetime
from src.databases.database import get_connection
from src.util.id_generator import generate_complaint_id


def generate_complaint_id():
    return "GOV-" + str(uuid.uuid4())[:6].upper()


def predict_complaint_priority(text: str):

    text = text.lower()

    high_keywords = [
        "urgent", "immediately", "emergency",
        "fraud", "danger", "critical",
        "fire", "accident"
    ]

    medium_keywords = [
        "delay", "not working", "problem",
        "issue", "slow", "damage", "broken"
    ]

    for word in high_keywords:
        if word in text:
            return "High"

    for word in medium_keywords:
        if word in text:
            return "Medium"

    return "Low"


def register_complaint(description, location="Not Provided", department="General"):

    complaint_id = generate_complaint_id()
    priority = predict_complaint_priority(description)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    complaint_id = generate_complaint_id()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_id,
        description,
        location,
        department,
        priority,
        "Pending",
        created_at
    ))

    conn.commit()
    conn.close()

    return complaint_id, priority


def get_complaint_status(complaint_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM complaints WHERE complaint_id=?",
        (complaint_id,)
    )

    complaint = cursor.fetchone()

    conn.close()

    return complaint