
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

def fetch_isin_nse(query):
    """Fetch ISIN from NSE India search API"""
    url = "https://www.nseindia.com/api/search/autocomplete"
    params = {"q": query}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    }
    
    try:
        # NSE requires session cookies
        session = requests.Session()
        # First visit homepage to get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        # Then search
        response = session.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        symbols = data.get("symbols", [])
        
        for item in symbols:
            symbol_name = item.get("symbol_info", "")
            if is_name_match(query, symbol_name):
                # Get ISIN from symbol detail
                symbol = item.get("symbol", "")
                if symbol:
                    # Fetch quote to get ISIN
                    quote_url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
                    quote_resp = session.get(quote_url, headers=headers, timeout=10)
                    if quote_resp.status_code == 200:
                        quote_data = quote_resp.json()
                        isin = quote_data.get("info", {}).get("isin")
                        if isin:
                            return isin, "NSE India API"
    except Exception as e:
        print(f"Error in NSE search: {e}")
    
    return None, None


def fetch_isin_moneycontrol_autosuggest(query):
    # Try generic search (no type) or specific types
    # Type 1 = Stocks
    # Type 4 = Mutual Funds (maybe? let's try generic)
    
    # We will try to search and if we get a link, we visit it.
    # If we get a direct ISIN in the name, we use it.
    
    # First try generic/stock search
    url = f"https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&query={query}&type=1&format=json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.moneycontrol.com/",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Check if response is empty
        if not response.text or response.text.strip() == "":
            print(f"MC autosuggest returned empty response for: {query}")
            return None, None
            
        data = response.json()
        
        # Check if data is a list
        if not isinstance(data, list):
            print(f"MC autosuggest returned non-list data for: {query}")
            return None, None
            
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
    except requests.exceptions.RequestException as e:
        print(f"Network error in MC autosuggest: {e}")
    except ValueError as e:
        print(f"JSON decode error in MC autosuggest: {e}")
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
    # Strategy 1: NSE India API (Most reliable for stocks)
    isin, source = fetch_isin_nse(query)
    if isin:
        return {"isin": isin, "source": source, "query": query}
    
    # Strategy 2: Moneycontrol Autosuggest (Fast, but may be blocked)
    isin, source = fetch_isin_moneycontrol_autosuggest(query)
    if isin:
        return {"isin": isin, "source": source, "query": query}
        
    # Strategy 3: DDG Search (General fallback)
    isin, source = fetch_isin_ddg(query)
    if isin:
        return {"isin": isin, "source": source, "query": query}
        
    return {"isin": None, "source": "Not Found", "query": query}

