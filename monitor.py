import requests
from bs4 import BeautifulSoup

OCPF_URL = "https://www.ocpf.us/Reports/Log"

def fetch_governor_filings():
    r = requests.get(OCPF_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("table.table tbody tr")
    filings = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 5:
            continue

        date, committee, office, report_type, total = cols[:5]

        if "governor" not in office.lower():
            continue

        link_tag = row.find("a")
        url = None
        filing_id = None

        if link_tag and "href" in link_tag.attrs:
            url = "https://www.ocpf.us" + link_tag["href"]
            filing_id = link_tag["href"].split("/")[-1]

        filings.append({
            "id": filing_id,
            "date": date,
            "committee": committee,
            "office": office,
            "type": report_type,
            "total": total,
            "url": url,
        })

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

    if last_id is None:
        print("First run — storing state.")
        save_last_id(newest)
        return

    new_filings = []
    for f in filings:
        if f["id"] == last_id:
            break
        new_filings.append(f)

    if new_filings:
        print("NEW GOVERNOR FILINGS:")
        for f in new_filings:
            print(f"- {f['date']} | {f['committee']} | {f['type']} | {f['url']}")
    else:
        print("No new governor filings.")

    save_last_id(newest)

if __name__ == "__main__":
    main()
