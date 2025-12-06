#!/usr/bin/env python3
"""
Simple test client for the ISIN Fetcher API
"""

import requests
import json

def test_isin_api():
    url = "http://localhost:8000/fetch-isins"
    
    # Test queries
    queries = [
        "Amara Raja Energy & Mobility",  # ARE&M
        "Bharat Electronics",  # BEL
        "Cochin Shipyard",  # COCHINSHIP
        "Divi's Laboratories",  # DIVISLAB
        "Dr Reddy's Laboratories",  # DRREDDY
        "Federal Bank",  # FEDERALBNK
        "Finolex Cables",  # FINCABLES
        "Gold BeES",  # GOLDBEES
        "Hero MotoCorp",  # HEROMOTOCO
        "ICICI Lombard General Insurance",  # ICICIGI
        "ICICI Prudential Life Insurance",  # ICICIPRULI
        "IDFC First Bank",  # IDFCFIRSTB
        "IndusInd Bank",  # INDUSINDBK
        "IT BeES",  # ITBEES
        "ITC Limited",  # ITC
        "ITC Hotels",  # ITCHOTELS
        "Jyothy Labs",  # JYOTHYLAB
        "Kovai Medical Center",  # KOVAI
        "KOTAK PENSION FUND SCHEME",
        "HDFC PENSION MANAGEMENT COMPANY LIMITED SCHEME"
    ]
    
    payload = {"queries": queries}
    
    print("Testing ISIN Fetcher API...")
    print(f"Sending queries: {queries}\n")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        results = response.json()
        
        print("Results:")
        print("=" * 80)
        for result in results:
            print(f"\nQuery: {result['query']}")
            print(f"ISIN:  {result['isin']}")
            print(f"Source: {result['source']}")
        print("\n" + "=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running with: python3 main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_isin_api()
