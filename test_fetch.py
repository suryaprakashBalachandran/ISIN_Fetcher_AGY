
import requests
from bs4 import BeautifulSoup
import re

def search_isin_google(query):
    # This is a bit fragile as it relies on Google's HTML structure or a library.
    # Let's try a financial site search instead, e.g., Moneycontrol.
    pass

def search_moneycontrol(query):
    results = []
    # Try types 1 (Stocks) and 4 (Mutual Funds) - guessing the codes
    # Actually, let's try to fetch without type or check response structure
    # Common types: 1=Stock, 2=Index?, 3=?, 4=MF?
    for type_id in [1, 4]: 
        url = f"https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&query={query}&type={type_id}&format=json"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = response.json()
            for item in data:
                # Add type info to result
                item['type_id'] = type_id
                results.append(item)
        except Exception as e:
            print(f"Error fetching type {type_id}: {e}")
    return results

def get_isin_from_moneycontrol_url(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        # ISIN is usually in the page content.
        # Common pattern: "ISIN: INE..."
        text = soup.get_text()
        match = re.search(r'ISIN\s*[:\-\s]\s*([A-Z0-9]{12})', text, re.IGNORECASE)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error fetching url {url}: {e}")
    return None

if __name__ == "__main__":
    queries = ["Tata Motors", "Parag Parikh Flexi Cap"]
    for q in queries:
        print(f"Searching for {q}...")
        results = search_moneycontrol(q)
        for res in results[:3]: # Print top 3
            print(f"Type: {res.get('type_id')} | Name: {res.get('pdt_dis_nm')} | Link: {res.get('link_src')}")
            if res.get('link_src'):
                isin = get_isin_from_moneycontrol_url(res.get('link_src'))
                print(f"  -> ISIN: {isin}")
