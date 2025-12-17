import os
import requests
import smtplib
from email.mime.text import MIMEText

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

RECIPIENT_EMAIL = "YOUR_EMAIL_HERE"     # where alerts are sent
SENDER_EMAIL = "YOUR_GMAIL_ADDRESS"     # same as daily digest

SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# REAL endpoint for newly organized candidate committees
REG_API_URL = "https://api.ocpf.us/filers/recentlyOrganized/C?officeFilter="

STATE_FILE = "registration_state.txt"


# -------------------------------------------------------------------
# CORE FUNCTIONS
# -------------------------------------------------------------------

def load_last_id():
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_id(last_id):
    with open(STATE_FILE, "w") as f:
        f.write(last_id)


def fetch_new_committees():
    """Fetch newly organized candidate committees from OCPF API."""
    r = requests.get(REG_API_URL)
    r.raise_for_status()
    data = r.json()   # This should be a list

    committees = []
    for item in data:
        # We will adjust these once we see real JSON
        committee_id = str(item.get("cpfId", ""))
        name = item.get("fullNameReverse", "") or item.get("name", "")
        office_sought = item.get("officeSought", "")
        created_date = item.get("dateFiled", "") or item.get("organizeDate", "")

        committees.append({
            "id": committee_id,
            "name": name,
            "office": office_sought,
            "date": created_date,
        })

    return committees


def send_email(subject, body):
    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD not set.")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)


def main():
    last_id = load_last_id()
    committees = fetch_new_committees()

    if not committees:
        print("API returned no committees.")
        return

    # Assume newest first
    newest_id = committees[0]["id"]

    # Print recent items for debugging
    print("=== MOST RECENT 5 REGISTRATIONS (raw) ===")
    for c in committees[:5]:
        print(f"- {c['date']} | {c['name']} | {c['office']} | id={c['id']}")
    print("=========================================\n")

    if last_id is None:
        print("First run — initializing state.")
        save_last_id(newest_id)
        return

    # Identify new items
    new_items = []
    for c in committees:
        if c["id"] == last_id:
            break
        new_items.append(c)

    if not new_items:
        print("No new committee registrations.")
        save_last_id(newest_id)
        return

    # Build email
    lines = [
        f"- {c['date']} | {c['name']} | {c['office']} | ID: {c['id']}"
        for c in new_items
    ]
    body = "New committee registrations:\n\n" + "\n".join(lines)
    subject = "New OCPF Committee Registrations"

    send_email(subject, body)
    print(f"Sent email for {len(new_items)} new registrations.")

    save_last_id(newest_id)


if __name__ == "__main__":
    main()
