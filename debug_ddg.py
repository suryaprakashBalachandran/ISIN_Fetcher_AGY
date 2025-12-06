
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import re

def debug_ddg(query):
    search_query = f"{query} ISIN"
    print(f"Searching: {search_query}")
    results = DDGS().text(search_query, max_results=5)
    for res in results:
        print(f"Title: {res['title']}")
        print(f"URL: {res['href']}")
        print(f"Snippet: {res['body'][:100]}...")
        
        if "moneycontrol.com" in res['href']:
            print("  Visiting Moneycontrol link...")
            try:
                page_resp = requests.get(res['href'], headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                if page_resp.status_code == 200:
                    text = page_resp.text
                    match = re.search(r'ISIN\s*[:\-\s]\s*([A-Z0-9]{12})', text, re.IGNORECASE)
                    if match:
                        print(f"  Found ISIN: {match.group(1)}")
                    else:
                        print("  No ISIN found on page.")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    debug_ddg("Paragh pariek flexi cap fund")
