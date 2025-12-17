import requests

# Pull enough results to include the latest governor filings
API_URL = "https://api.ocpf.us/reports/log?name=&pageSize=2000"


def fetch_governor_filings():
    r = requests.get(API_URL)
    r.raise_for_status()

    data = r.json()  # list of filings
    filings = []

    for item in data:
        office = (item.get("officeSought") or "").strip().lower()

        # Filter: EXACTLY "Governor"
        if office != "governor":
            continue

        filing_id = str(item.get("reportId", ""))
        date = item.get("dateFiled", "")
        committee = item.get("fullNameReverse", "")
        report_type = item.get("reportTypeDescription", "")
        period = item.get("reportingPeriod", "")
        receipts = item.get("receiptTotal", "")
        expenditures = item.get("expenditureTotal", "")
        url = item.get("reportLink")

        filings.append({
            "id": filing_id,
            "date": date,
            "committee": committee,
            "office": office,
            "type": f"{report_type} ({period})",
            "receipts": receipts,
            "expenditures": expenditures,
            "url": url,
        })

    # API is naturally sorted by newest first — but let's enforce it
    filings.sort(key=lambda f: f["date"], reverse=True)

    return filings


def load_last_id():
    try:
        with open("state.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_id(last_id):
    with open("state.txt", "w") as f:
        f.write(last_id)


def main():
    last_id = load_last_id()
    filings = fetch_governor_filings()

    if not filings:
        print("No governor filings found.")
        return

    newest = filings[0]["id"]

    # ---- ALWAYS SHOW THE LAST 5 GOVERNOR FILINGS ----
    print("=== MOST RECENT 5 GOVERNOR FILINGS ===")
    for f in filings[:5]:
        print(f"- {f['date']} | {f['committee']} | {f['type']} | {f['url']}")
    print("======================================\n")
    # -------------------------------------------------

    if last_id is None:
        print("First run — storing state.")
        save_last_id(newest)
        return

    # Determine new filings
    new_filings = []
    for f in filings:
        if f["id"] == last_id:
            break
        new_filings.append(f)

    if new_filings:
        print("NEW GOVERNOR FILINGS:")
        for f in new_filings:
            print(
                f"- {f['date']} | {f['committee']} | "
                f"{f['type']} | receipts: {f['receipts']} "
                f"| expenditures: {f['expenditures']} | {f['url']}"
            )
    else:
        print("No new governor filings.")

    save_last_id(newest)


if __name__ == "__main__":
    main()
