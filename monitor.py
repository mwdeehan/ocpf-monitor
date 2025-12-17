import requests
import json

API_URL = "https://api.ocpf.us/reports/log?name=&pageSize=50"


def main():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()

    print("=== DEBUG SAMPLE ===")
    print(f"Type of data: {type(data)}")
    print(f"Length: {len(data)}")
    print()

    # Print first 10 items clearly
    for i, item in enumerate(data[:10]):
        print(f"--- ITEM {i} ---")
        print(json.dumps(item, indent=2))
        print()

    print("=== END DEBUG ===")


if __name__ == "__main__":
    main()
