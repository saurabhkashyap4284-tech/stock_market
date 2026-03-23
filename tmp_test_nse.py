import requests
import json

url = "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"
headers = {
    "accept": "*/*",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "dnt": "1",
    "priority": "u=1, i",
    "referer": "https://www.nseindia.com/market-data/oi-spurts",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}

# NSE usually needs a session from the main page first
session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

try:
    response = session.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2)[:2000]) # Print first 2000 chars
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
