import fetch_fda

print("Testing Paracetamol (Should map to Acetaminophen)...")
res = fetch_fda.fetch_drug_label("Paracetamol")
if res: 
    print("SUCCESS: Found data for Paracetamol")
else:
    print("FAILURE: Paracetamol not found")

print("\nTesting CardioXin (Should map to Digoxin)...")
res = fetch_fda.fetch_drug_label("CardioXin")
if res:
    print("SUCCESS: Found data for CardioXin")
else:
    print("FAILURE: CardioXin not found")
