import os
import requests
import smtplib
from email.mime.text import MIMEText

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

RECIPIENT_EMAIL = "YOUR_EMAIL_HERE"      # where alerts are sent
SENDER_EMAIL = "YOUR_GMAIL_ADDRESS"      # same as daily_digest.py
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

REG_API_URL = "https://api.ocpf.us/filers/recentlyOrganized/C?officeFilter="

STATE_FILE = "registration_state.txt"

# Optional: filter only governor committees
FILTER_GOVERNOR_ONLY = False   # set to True if you want only Governor filings


# -------------------------------------------------------------------
# UTILITIES
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


def send_email(subject, body):
    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is not set")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)


# -------------------------------------------------------------------
# CORE LOGIC
# -------------------------------------------------------------------

def fetch_registrations():
    r = requests.get(REG_API_URL)
    r.raise_for_status()
    data = r.json()  # list

    committees = []
    for item in data:
        office = item.get("officeSoughtDescription", "")

        if FILTER_GOVERNOR_ONLY and office.lower() != "governor":
            continue

        committees.append({
            "id": str(item.get("cpfId")),
            "date": item.get("organizationDate", ""),
            "name": item.get("fullNameReverse", ""),
            "office": office,
            "pdf": item.get("organizationStatementBlobUrl", ""),
        })

    return committees


def main():
    last_id = load_last_id()
    committees = fetch_registrations()

    if not committees:
        print("No committee registrations returned from API.")
        return

    newest_id = committees[0]["id"]

    # FIRST RUN → Initialize state, don't send emails
    if last_id is None:
        print("First run — storing initial registration state.")
        save_last_id(newest_id)
        return

    # Identify new registrations
    new_items = []
    for c in committees:
        if c["id"] == last_id:
            break
        new_items.append(c)

    if not new_items:
        print("No new registrations.")
        save_last_id(newest_id)
        return

    # Build email
    lines = []
    for c in new_items:
        lines.append(
            f"- {c['date']} | {c['name']} | {c['office']}\n  PDF: {c['pdf']}"
        )

    body = "New candidate committee registrations:\n\n" + "\n".join(lines)

    send_email("New OCPF Candidate Committee Registrations", body)

    print(f"Sent email alert for {len(new_items)} new registrations.")

    save_last_id(newest_id)


if __name__ == "__main__":
    main()
