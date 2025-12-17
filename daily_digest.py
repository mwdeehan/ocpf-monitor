import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

API_URL = "https://api.ocpf.us/reports/log?name=&pageSize=2000"

# -------- EDIT THIS --------
RECIPIENT_EMAIL = "YOUR_EMAIL_HERE"
SENDER_EMAIL = "YOUR_GMAIL_ADDRESS"
# ----------------------------

def fetch_governor_filings():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()

    filings = []
    for item in data:
        office = (item.get("officeSought") or "").strip().lower()
        if office != "governor":
            continue

        filings.append({
            "id": str(item.get("reportId", "")),
            "date": item.get("dateFiled", ""),
            "committee": item.get("fullNameReverse", ""),
            "type": item.get("reportTypeDescription", ""),
            "period": item.get("reportingPeriod", ""),
            "receipts": item.get("receiptTotal", ""),
            "expenditures": item.get("expenditureTotal", ""),
            "url": item.get("reportLink"),
        })

    return filings


def filter_last_24_hours(filings):
    """Select filings filed within the last 24 hours."""
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)

    results = []
    for f in filings:
        try:
            filed_dt = datetime.strptime(f["date"], "%a, %m/%d/%Y %I:%M %p")
        except ValueError:
            continue

        if filed_dt >= cutoff:
            results.append(f)

    return results


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    # SMTP using Gmail App Password
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)


def main():
    filings = fetch_governor_filings()
    recent = filter_last_24_hours(filings)

    if not recent:
        body = "No governor filings in the last 24 hours."
    else:
        lines = []
        for f in recent:
            lines.append(
                f"- {f['date']} | {f['committee']} | {f['type']} ({f['period']}) "
                f"| Receipts: {f['receipts']}, Expenditures: {f['expenditures']}\n  {f['url']}"
            )
        body = "\n".join(lines)

    subject = "Daily OCPF Governor Filings Digest"
    send_email(subject, body)


if __name__ == "__main__":
    # Placeholder: GitHub injects SMTP_PASSWORD as an environment variable
    import os
    global SMTP_PASSWORD
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    main()
