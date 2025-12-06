
from mftool import Mftool
import json

def check_mftool(query):
    obj = Mftool()
    # Search for schemes
    schemes = obj.get_scheme_codes()
    # Filter by name
    matches = {k: v for k, v in schemes.items() if query.lower() in v.lower()}
    print(f"Found {len(matches)} matches for {query}")
    
    for code, name in list(matches.items())[:3]:
        print(f"Code: {code}, Name: {name}")
        # Get details
        details = obj.get_scheme_details(code)
        # details is a dict with 'meta' and 'data'
        meta = details.get('meta', {})
        data = details.get('data', [])
        print(f"  Meta: {meta}")
        # print(f"  Data sample: {data[:1] if data else 'No data'}")
        
        # Sometimes ISIN is in the meta under a different key or I missed it.
        # Let's print the whole meta.

if __name__ == "__main__":
    check_mftool("Parag Parikh Flexi Cap")
