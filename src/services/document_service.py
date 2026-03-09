import sqlite3

def verify_document(document_id):

    conn = sqlite3.connect("egov.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT owner_name, document_type, status FROM documents WHERE document_id=?",
        (document_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        owner, doc_type, status = result
        return f"""
Document Details
Owner: {owner}
Type: {doc_type}
Status: {status}
"""
    else:
        return "Document not found."