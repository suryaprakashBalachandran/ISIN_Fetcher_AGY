
import requests
from bs4 import BeautifulSoup
import re
from duckduckgo_search import DDGS

def get_isin_from_text(text, prefer_fund=False):
    # Standard ISIN regex: 2 letters, 9 alphanum, 1 digit
    
    # Find all matches
    # ISIN is 12 chars. Indian ISINs start with INE, INF, IN9.
    # So we need 3 chars prefix + 9 chars suffix = 12 chars.
    matches = re.findall(r'\b((?:INE|INF|IN9)[A-Z0-9]{9})\b', text)
    if not matches:
        # Try looser regex
        matches = re.findall(r'ISIN\s*[:\-\s]\s*([A-Z0-9]{12})', text, re.IGNORECASE)
        
    if not matches:
        return None
        
    unique_matches = list(set(matches))
    
    if prefer_fund:
        # Look for INF first
        inf_matches = [m for m in unique_matches if m.startswith('INF')]
        if inf_matches:
            return inf_matches[0]
            
    # Default: return first (or INE if present and we don't prefer fund)
    return unique_matches[0]

def is_name_match(query, result_name):
    # Simple token overlap
    q_tokens = set([t for t in re.findall(r'\w+', query.lower()) if len(t) > 2])
    r_tokens = set([t for t in re.findall(r'\w+', result_name.lower()) if len(t) > 2])
    
    if not q_tokens: # Short query like "PV"?
        return True
        
    # Calculate overlap
    common = q_tokens.intersection(r_tokens)
    if not common:
        return False
        
    return True

def fetch_isin_moneycontrol_autosuggest(query):
    # Try generic search (no type) or specific types
    # Type 1 = Stocks
    # Type 4 = Mutual Funds (maybe? let's try generic)
    
    # We will try to search and if we get a link, we visit it.
    # If we get a direct ISIN in the name, we use it.
    
    # First try generic/stock search
    url = f"https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&query={query}&type=1&format=json"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        for item in data:
            name_html = item.get("pdt_dis_nm", "")
            # Clean name for validation (remove html tags)
            clean_name = re.sub(r'<[^>]+>', '', name_html)
            # Also remove the ISIN part from name for matching
            name_only = clean_name.split("INE")[0].split("INF")[0]
            
            if is_name_match(query, name_only):
                prefer_fund = "fund" in query.lower() or "scheme" in query.lower()
                isin = get_isin_from_text(name_html, prefer_fund=prefer_fund)
                if isin:
                    return isin, "Moneycontrol Autosuggest"
    except Exception as e:
        print(f"Error in MC autosuggest: {e}")
        
    return None, None

def fetch_isin_ddg(query):
    # Search for "{Query} ISIN"
    search_query = f"{query} ISIN"
    try:
        results = DDGS().text(search_query, max_results=3)
        for res in results:
            # Check snippet first
            snippet = res['body'] + " " + res['title']
            prefer_fund = "fund" in query.lower() or "scheme" in query.lower()
            isin = get_isin_from_text(snippet, prefer_fund=prefer_fund)
            if isin:
                return isin, "DDG Snippet"
            
            # Visit URL
            url = res['href']
            try:
                # specific handling for moneycontrol urls as they are reliable
                if "moneycontrol.com" in url or "screener.in" in url or "amfiindia.com" in url:
                    page_resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                    if page_resp.status_code == 200:
                        isin = get_isin_from_text(page_resp.text, prefer_fund=prefer_fund)
                        if isin:
                            return isin, f"Scraped {url}"
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                
    except Exception as e:
        print(f"Error in DDG: {e}")
        
    # Fallback: Search without "ISIN" to see if we can find a relevant page (e.g. Moneycontrol)
    # and then scrape it.
    if "ISIN" in search_query:
        try:
            print(f"Retrying DDG without 'ISIN' keyword for {query}")
            results = DDGS().text(query, max_results=3)
            for res in results:
                url = res['href']
                if "moneycontrol.com" in url or "screener.in" in url or "amfiindia.com" in url:
                    try:
                        page_resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                        if page_resp.status_code == 200:
                            prefer_fund = "fund" in query.lower() or "scheme" in query.lower()
                            isin = get_isin_from_text(page_resp.text, prefer_fund=prefer_fund)
                            if isin:
                                return isin, f"Scraped {url} (Fallback)"
                    except:
                        pass
        except:
            pass
            
    return None, None

def fetch_isin(query):
    # Strategy 1: Moneycontrol Autosuggest (Fast, good for stocks)
    isin, source = fetch_isin_moneycontrol_autosuggest(query)
    if isin:
        return {"isin": isin, "source": source, "query": query}
        
    # Strategy 2: DDG Search (General fallback)
    isin, source = fetch_isin_ddg(query)
    if isin:
        return {"isin": isin, "source": source, "query": query}
        
    return {"isin": None, "source": "Not Found", "query": query}
