import os
import requests
import smtplib
from email.mime.text import MIMEText

RECIPIENT_EMAIL = "YOUR_EMAIL_HERE"
SENDER_EMAIL = "YOUR_GMAIL_ADDRESS"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

AMEND_API = "https://api.ocpf.us/filers/recentlyAmended/C?officeFilter="
TERM_API  = "https://api.ocpf.us/filers/recentlyTerminated/C?officeFilter="

AMEND_STATE = "amend_state.txt"
TERM_STATE  = "term_state.txt"


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)


def load_state(file):
    try:
        with open(file, "r") as f:
            return f.read().strip()
    except:
        return None


def save_state(file, last_id):
    with open(file, "w") as f:
        f.write(last_id)


def fetch(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def extract(items, date_field):
    """Convert API objects into a uniform structure."""
    output = []
    for item in items:
        output.append({
            "id": str(item.get("cpfId")),
            "name": item.get("fullNameReverse", ""),
            "office": item.get("officeSoughtDescription", ""),
            "date": item.get(date_field, ""),
        })
    return output


def process(category, api_url, state_file, date_field):
    data = fetch(api_url)
    items = extract(data, date_field)

    if not items:
        print(f"No {category} returned.")
        return

    newest = items[0]["id"]
    last = load_state(state_file)

    print(f"=== LATEST 5 {category.upper()} ===")
    for x in items[:5]:
        print(f"- {x['date']} | {x['name']} | {x['office']} | id={x['id']}")
    print("=" * 40)

    if last is None:
        print(f"Initializing {category} state.")
        save_state(state_file, newest)
        return

    new_items = []
    for x in items:
        if x["id"] == last:
            break
        new_items.append(x)

    if new_items:
        body = f"New committee {category}:\n\n"
        for x in new_items:
            body += f"- {x['date']} | {x['name']} | {x['office']} | id={x['id']}\n"

        send_email(f"New OCPF Committee {category.title()}", body)
        print(f"Sent {category} alerts.")
    else:
        print(f"No new committee {category}.")

    save_state(state_file, newest)


def main():
    process("amendments", AMEND_API, AMEND_STATE, "amendmentDate")
    process("terminations", TERM_API, TERM_STATE, "terminationDate")


if __name__ == "__main__":
    main()
