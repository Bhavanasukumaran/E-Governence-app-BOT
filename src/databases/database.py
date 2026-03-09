import sqlite3

DB_NAME = "complaints.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """
    Create complaints table if it does not exist
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id TEXT PRIMARY KEY,
        description TEXT,
        location TEXT,
        department TEXT,
        priority TEXT,
        status TEXT,
        created_at TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id TEXT UNIQUE,
        owner_name TEXT,
        document_type TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()