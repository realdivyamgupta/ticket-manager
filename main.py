import sqlite3

DB_NAME = "tickets.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            priority INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL,
            sla_deadline TEXT NOT NULL,
            resolved_at TEXT
        )
    """)
    conn.commit()
    conn.close()

    if __name__ == "__main__":
    init_db()
    print("Database created successfully.")