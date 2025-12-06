
from duckduckgo_search import DDGS
import re
import requests
from bs4 import BeautifulSoup

def search_isin_hybrid(query):
    # Search for the moneycontrol page
    search_query = f"site:moneycontrol.com {query} ISIN"
    print(f"Searching DDG for: {search_query}")
    results = DDGS().text(search_query, max_results=3)
    
    for res in results:
        url = res['href']
        print(f"Checking URL: {url}")
        # Scrape the page
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                # Look for ISIN
                match = re.search(r'ISIN\s*[:\-\s]\s*([A-Z0-9]{12})', text, re.IGNORECASE)
                if match:
                    return match.group(1)
                
                # Sometimes it's in a specific element
                # e.g. <span class="isin">INE...</span>
                # But regex on text usually catches it.
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    return None

if __name__ == "__main__":
    queries = ["Tata Motors", "Parag Parikh Flexi Cap Fund", "NPS Tier 1 Scheme G"]
    for q in queries:
        print(f"--- Processing {q} ---")
        isin = search_isin_hybrid(q)
        print(f"Result: {isin}")
