import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import json

RECIPIENT_EMAIL = "YOUR_EMAIL_HERE"
SENDER_EMAIL = "YOUR_GMAIL_ADDRESS"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

REG_API_URL = "https://api.ocpf.us/filers/recentlyOrganized/C?officeFilter="


def fetch_registrations():
    r = requests.get(REG_API_URL)
    r.raise_for_status()
    return r.json()  # list of committees


def filter_last_24_hours(items):
    results = []
    cutoff = datetime.utcnow() - timedelta(hours=24)

    for item in items:
        raw_date = item.get("organizationDate")
        if not raw_date:
            continue
        try:
            dt = datetime.strptime(raw_date, "%m/%d/%Y")
        except:
            continue
        if dt >= cutoff:
            results.append(item)

    return results


def format_digest(committees):
    if not committees:
        return "No committee registrations in the last 24 hours."

    lines = []
    for item in committees:
        name = item.get("fullNameReverse", "Unknown")
        office = item.get("officeSoughtDescription", "")
        date = item.get("organizationDate", "Unknown")
        pdf = item.get("organizationStatementBlobUrl", "")

        lines.append(
            f"- {date} | {name} | {office}\n  PDF: {pdf}"
        )

    return "\n".join(lines)


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)


def main():
    data = fetch_registrations()
    recent = filter_last_24_hours(data)

    body = format_digest(recent)
    send_email("Daily OCPF Registration Digest", body)
    print("Daily registration digest sent.")


if __name__ == "__main__":
    main()
