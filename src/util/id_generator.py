import uuid


def generate_complaint_id():
    """
    Generate unique complaint ID

    Example:
    GOV-3F82A1
    """

    return "GOV-" + str(uuid.uuid4())[:6].upper()