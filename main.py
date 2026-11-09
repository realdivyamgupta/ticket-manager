import os
import webbrowser
from report import generate_dashboard
from db import init_db, tickets_per_category, avg_resolution_hours, sla_breaches
from tickets import (
    create_ticket,
    get_all_tickets,
    get_next_ticket,
    resolve_ticket,
    load_heap,
    PRIORITY_NAMES,
)


def show_tickets(rows):
    if not rows:
        print("No tickets found.")
        return
    print(f"{'ID':<4}{'Title':<30}{'Category':<12}{'Priority':<10}{'Status':<13}{'SLA Deadline'}")
    for r in rows:
        print(f"{r[0]:<4}{r[1]:<30}{r[2]:<12}{PRIORITY_NAMES[r[3]]:<10}{r[4]:<13}{r[6]}")


def ask_priority():
    while True:
        try:
            p = int(input("Priority (1=Critical, 2=High, 3=Medium, 4=Low): "))
            if p in PRIORITY_NAMES:
                return p
        except ValueError:
            pass
        print("Please enter a number from 1 to 4.")


def main():
    init_db()
    load_heap()
    while True:
        print("\n--- Support Ticket Manager ---")
        print("1. Create ticket")
        print("2. View all tickets")
        print("3. Get next ticket to work on")
        print("4. Resolve ticket")
        print("5. Show reports")
        print("6. Generate HTML dashboard")
        print("7. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            title = input("Title: ").strip()
            category = input("Category (e.g. Email, Network, Hardware): ").strip()
            if not title or not category:
                print("Title and category cannot be empty.")
                continue
            priority = ask_priority()
            tid = create_ticket(title, category, priority)
            print(f"Ticket {tid} created.")
        elif choice == "2":
            show_tickets(get_all_tickets())
        elif choice == "3":
            ticket = get_next_ticket()
            if ticket:
                print("Next ticket to work on:")
                show_tickets([ticket])
            else:
                print("No open tickets.")
        elif choice == "4":
            try:
                tid = int(input("Ticket ID to resolve: "))
                resolve_ticket(tid)
                print("Ticket resolved.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "5":
            print("\nTickets per category:")
            for category, count in tickets_per_category():
                print(f"  {category}: {count}")
            avg = avg_resolution_hours()
            print("Average resolution time:",
                  f"{avg:.2f} hours" if avg is not None else "no resolved tickets yet")
            print("SLA breaches:", sla_breaches() or "none")
        elif choice == "6":
            path = generate_dashboard()
            webbrowser.open("file://" + os.path.abspath(path))
            print("Dashboard generated:", path)
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()