import requests
import json
import os

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_DIR, "fda_context.json")

# Map Fake Brand Name -> Real Ingredient
DRUG_MAP = {
    "Wegovy": "semaglutide",
    "Leqembi": "lecanemab",
    "Mounjaro": "tirzepatide",
    "Skyrizi": "risankizumab",
    "Paxlovid": "nirmatrelvir",
    "Rinvoq": "upadacitinib",
    "CardioXin": "digoxin",
    "Paracetamol": "acetaminophen"
}

def fetch_drug_label(drug_name):
    """
    Fetches official FDA label. 
    Handles Brand -> Generic mapping locally before querying.
    """
    # 1. Normalize & Map
    search_term = drug_name.lower().strip()
    
    # Direct Mapping (Custom Demo & Real World)
    # Check if the lowercased drug_name matches any lowercased key in DRUG_MAP
    mapped_ingredient = None
    for brand, ingredient in DRUG_MAP.items():
        if brand.lower() == search_term:
            mapped_ingredient = ingredient
            break
    
    if mapped_ingredient:
        search_term = mapped_ingredient
        
    print(f"DEBUG: Fetching OpenFDA for '{search_term}' (Original: '{drug_name}')")

    # 2. Query OpenFDA
    try:
        # Strategy A: Try Exact Brand Name
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:\"{search_term}\"+OR+openfda.generic_name:\"{search_term}\"&limit=1"
        r = requests.get(url, timeout=5)
        
        if r.status_code != 200:
            # Strategy B: Fuzzy Search
            url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{search_term}+OR+openfda.generic_name:{search_term}&limit=1"
            r = requests.get(url, timeout=5)

        if r.status_code == 200:
            data = r.json()
            if "results" in data:
                res = data["results"][0]
                return {
                    "source": "OpenFDA",
                    "brand": res.get("openfda", {}).get("brand_name", [drug_name])[0],
                    "generic": res.get("openfda", {}).get("substance_name", ["Unknown"])[0],
                    "warnings": res.get("warnings", ["No boxed warnings."])[0],
                    "adverse_reactions": res.get("adverse_reactions", ["No side effects listed."])[0],
                    "indications": res.get("indications_and_usage", ["No indications listed."])[0]
                }
    except Exception as e:
        print(f"DEBUG: Error fetching {url} - {e}")
        return None
            
    return None

def main():
    print("Fetching OpenFDA Data...")
    fda_db = {}
    
    for brand, ingredient in DRUG_MAP.items():
        print(f" - Querying for {brand} ({ingredient})...")
        data = fetch_drug_label(ingredient)
        if data:
            fda_db[brand] = data
            print(f"   ✓ Found label.")
        else:
            print(f"   ✗ No data found.")
            
    with open(OUTPUT_FILE, "w") as f:
        json.dump(fda_db, f, indent=2)
    
    print(f"Saved FDA Context to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
