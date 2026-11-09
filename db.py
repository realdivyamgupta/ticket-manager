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

def tickets_per_category():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) FROM tickets GROUP BY category"
    ).fetchall()
    conn.close()
    return rows


def avg_resolution_hours():
    conn = get_connection()
    row = conn.execute(
        "SELECT AVG((julianday(resolved_at) - julianday(created_at)) * 24) "
        "FROM tickets WHERE status = 'Resolved'"
    ).fetchone()
    conn.close()
    return row[0]


def sla_breaches():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, priority, sla_deadline FROM tickets "
        "WHERE (status != 'Resolved' AND sla_deadline < datetime('now')) "
        "OR (status = 'Resolved' AND resolved_at > sla_deadline)"
    ).fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database created successfully.")