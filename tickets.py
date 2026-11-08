from datetime import datetime, timedelta, timezone
from db import get_connection

# priority -> hours allowed before the ticket breaches its SLA
SLA_HOURS = {1: 4, 2: 8, 3: 24, 4: 72}
PRIORITY_NAMES = {1: "Critical", 2: "High", 3: "Medium", 4: "Low"}
FMT = "%Y-%m-%d %H:%M:%S"


def now_utc():
    return datetime.now(timezone.utc)


def create_ticket(title, category, priority):
    now = now_utc()
    deadline = now + timedelta(hours=SLA_HOURS[priority])
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO tickets (title, category, priority, created_at, sla_deadline) "
        "VALUES (?, ?, ?, ?, ?)",
        (title, category, priority, now.strftime(FMT), deadline.strftime(FMT)),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id


def update_status(ticket_id, new_status):
    conn = get_connection()
    conn.execute(
        "UPDATE tickets SET status = ? WHERE id = ?",
        (new_status, ticket_id),
    )
    conn.commit()
    conn.close()


def resolve_ticket(ticket_id):
    conn = get_connection()
    conn.execute(
        "UPDATE tickets SET status = 'Resolved', resolved_at = ? WHERE id = ?",
        (now_utc().strftime(FMT), ticket_id),
    )
    conn.commit()
    conn.close()


def get_all_tickets():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()
    conn.close()
    return rows
