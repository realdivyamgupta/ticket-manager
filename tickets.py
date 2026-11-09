import heapq
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
    heapq.heappush(heap, (priority, deadline.strftime(FMT), ticket_id))
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

heap = []


def load_heap():
    """Load all Open tickets from the database into the heap."""
    heap.clear()
    conn = get_connection()
    rows = conn.execute(
        "SELECT priority, sla_deadline, id FROM tickets WHERE status = 'Open'"
    ).fetchall()
    conn.close()
    heap.extend(rows)
    heapq.heapify(heap)


def is_open(ticket_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT status FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()
    conn.close()
    return row is not None and row[0] == "Open"


def get_next_ticket():
    """Return the most urgent Open ticket and mark it In Progress."""
    while heap:
        priority, deadline, ticket_id = heapq.heappop(heap)
        if is_open(ticket_id):          # skip tickets resolved while in the heap
            update_status(ticket_id, "In Progress")
            conn = get_connection()
            row = conn.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ).fetchone()
            conn.close()
            return row
    return None
