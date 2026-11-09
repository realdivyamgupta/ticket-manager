import html
from datetime import datetime, timezone
from db import get_connection, tickets_per_category, avg_resolution_hours, sla_breaches
from tickets import PRIORITY_NAMES, FMT


def is_overdue(status, deadline):
    """A ticket is overdue if it is not resolved and its deadline has passed."""
    now = datetime.now(timezone.utc).strftime(FMT)
    return status != "Resolved" and deadline < now


def generate_dashboard():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, category, priority, status, sla_deadline "
        "FROM tickets ORDER BY priority, sla_deadline"
    ).fetchall()
    status_counts = dict(
        conn.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status").fetchall()
    )
    conn.close()

    total = len(rows)
    open_count = status_counts.get("Open", 0)
    in_progress = status_counts.get("In Progress", 0)
    resolved = status_counts.get("Resolved", 0)
    breaches = len(sla_breaches())
    avg = avg_resolution_hours()
    avg_text = f"{avg:.2f} hrs" if avg is not None else "N/A"

    # Bar chart: one bar per category, width relative to the largest count
    categories = tickets_per_category()
    max_count = max((count for _, count in categories), default=1)
    bars = ""
    for name, count in categories:
        width = int(count / max_count * 100)
        bars += (
            f'<div class="bar-row"><span class="bar-label">{html.escape(name)}</span>'
            f'<div class="bar" style="width:{width}%">{count}</div></div>\n'
        )

    # Ticket table rows
    table_rows = ""
    for tid, title, category, priority, status, deadline in rows:
        classes = f"p{priority}"
        if is_overdue(status, deadline):
            classes += " overdue"
        if status == "Resolved":
            classes += " resolved"
        table_rows += (
            f'<tr class="{classes}">'
            f"<td>{tid}</td>"
            f"<td>{html.escape(title)}</td>"
            f"<td>{html.escape(category)}</td>"
            f"<td>{PRIORITY_NAMES[priority]}</td>"
            f"<td>{status}</td>"
            f"<td>{deadline}</td>"
            f"</tr>\n"
        )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Support Ticket Dashboard</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<h1>Support Ticket Dashboard</h1>

<div class="cards">
  <div class="card"><h2>{total}</h2><p>Total</p></div>
  <div class="card"><h2>{open_count}</h2><p>Open</p></div>
  <div class="card"><h2>{in_progress}</h2><p>In Progress</p></div>
  <div class="card"><h2>{resolved}</h2><p>Resolved</p></div>
  <div class="card danger"><h2>{breaches}</h2><p>SLA Breaches</p></div>
  <div class="card"><h2>{avg_text}</h2><p>Avg Resolution</p></div>
</div>

<h2>Tickets by Category</h2>
{bars}

<h2>All Tickets (most urgent first)</h2>
<table>
  <tr><th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>SLA Deadline (UTC)</th></tr>
{table_rows}</table>
</body>
</html>
"""
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(page)
    return "dashboard.html"


if __name__ == "__main__":
    print("Dashboard written to", generate_dashboard())