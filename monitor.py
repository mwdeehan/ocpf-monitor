import requests
import json

API_URL = "https://api.ocpf.us/reports/log?name=&pageSize=2000"  # MUCH larger window

def main():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()

    governor_items = [item for item in data if (item.get("officeSought") or "").strip().lower() == "governor"]

    print(f"Found {len(governor_items)} governor filings in the last {len(data)} records.\n")

    # Show up to 10 of them
    for i, item in enumerate(governor_items[:10]):
        print(f"--- GOVERNOR ITEM {i} ---")
        print(json.dumps(item, indent=2))
        print()

if __name__ == "__main__":
    main()
