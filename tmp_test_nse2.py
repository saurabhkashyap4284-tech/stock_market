import requests
import json

urls = {
    "fo_securities": "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O",
    "live_derivatives": "https://www.nseindia.com/api/liveEquity-derivatives?index=sec_in_fno",
    "market_status": "https://www.nseindia.com/api/marketStatus",
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

for name, url in urls.items():
    try:
        res = session.get(url, headers=headers, timeout=10)
        print(f"\n--- {name} - Status: {res.status_code} ---")
        if res.status_code == 200:
            data = res.json()
            if "data" in data and len(data["data"]) > 0:
                print(f"Total items: {len(data['data'])}")
                print(json.dumps(data["data"][0], indent=2))
                
                if "oi" in data["data"][0] or "openInterest" in data["data"][0] or any("oi" in k.lower() for k in data["data"][0].keys()):
                    print("=> Has OI data")
                else:
                    print("=> NO OI data")
            elif name == "market_status":
                 print(json.dumps(data, indent=2))
        else:
            print(res.text[:200])
    except Exception as e:
        print(f"Error fetching {name}: {e}")
