from datetime import datetime
from src.databases.database import get_connection
from src.util.id_generator import generate_complaint_id


def predict_complaint_priority(text):

    text = text.lower()

    high_keywords = ["urgent", "danger", "critical", "emergency"]
    medium_keywords = ["delay", "problem", "issue", "not working"]

    for word in high_keywords:
        if word in text:
            return "High"

    for word in medium_keywords:
        if word in text:
            return "Medium"

    return "Low"


def register_complaint(description, location):

    complaint_id = generate_complaint_id()
    priority = predict_complaint_priority(description)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints
    (complaint_id, description, location, department, priority, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_id,
        description,
        location,
        "General",
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
        "SELECT status FROM complaints WHERE complaint_id=?",
        (complaint_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return "Complaint ID not found"