
import requests
import re

def probe_moneycontrol_types(query):
    for type_id in range(1, 10):
        url = f"https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&query={query}&type={type_id}&format=json"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = response.json()
            if data:
                print(f"Type {type_id} returned {len(data)} results.")
                print(f"  First result: {data[0]}")
        except Exception as e:
            pass

if __name__ == "__main__":
    probe_moneycontrol_types("Parag Parikh")
