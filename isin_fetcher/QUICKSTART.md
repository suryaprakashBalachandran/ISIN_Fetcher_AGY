# Quick Start Guide

## How to Run the ISIN Fetcher API

### Step 1: Start the Server

```bash
cd /Users/suryaprakash/.gemini/antigravity/playground/spatial-horizon/isin_fetcher
python3 main.py
```

The server will start on `http://localhost:8000`

### Step 2: Test the API

**Option A - Using the Python test client (Recommended):**

```bash
python3 test_client.py
```

**Option B - Using the shell script:**

```bash
./test_api.sh
```

**Option C - Using curl directly:**

```bash
curl -X POST "http://localhost:8000/fetch-isins" \
  -H "Content-Type: application/json" \
  -d '{"queries": ["tata motors PV", "Tata motors CV", "Parag Parikh Flexi Cap Fund"]}'
```

## Expected Output

```
Testing ISIN Fetcher API...
Sending queries: ['tata motors PV', 'Tata motors CV', 'Parag Parikh Flexi Cap Fund']

Results:
================================================================================

Query: tata motors PV
ISIN:  INE155A01022
Source: Moneycontrol Autosuggest

Query: Tata motors CV
ISIN:  INE155A01022
Source: Moneycontrol Autosuggest

Query: Parag Parikh Flexi Cap Fund
ISIN:  INF879O01019
Source: Scraped https://www.moneycontrol.com/mutual-funds/nav/parag-parikh-flexi-cap-fund-regular-plan/MPP001

================================================================================
```

## Using in Your Code

```python
import requests

url = "http://localhost:8000/fetch-isins"
payload = {
    "queries": [
        "Reliance Industries",
        "HDFC Bank",
        "SBI Bluechip Fund"
    ]
}

response = requests.post(url, json=payload)
results = response.json()

for result in results:
    print(f"{result['query']}: {result['isin']}")
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.
