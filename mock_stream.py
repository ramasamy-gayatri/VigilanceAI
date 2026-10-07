import csv
import time
import random
import os
import uuid
from datetime import datetime
from faker import Faker

fake = Faker()

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

# Files
SALES_FILE = os.path.join(DATA_DIR, "sales_stream.csv")
RX_FILE = os.path.join(DATA_DIR, "prescriptions_stream.csv")
SOCIAL_FILE = os.path.join(DATA_DIR, "social_stream.csv")

# Real Drugs (Modern Blockbusters)
DRUGS = ["Wegovy", "Leqembi", "Mounjaro", "Skyrizi", "Paxlovid", "Rinvoq"]
SOURCES = ["Reddit", "Twitter", "PubMed", "DoctorForum"]
ROLES = ["Patient", "Doctor", "Pharma Rep", "Pharmacist"]

# "Emerging Signals" - Risks NOT yet on the FDA Label (AI Discovery)
EMERGING_SIGNALS = {
    "Wegovy": ["Ozempic Face", "Hair Shedding", "Muscle Loss"],
    "Mounjaro": ["Thyroid Tenderness", "Severe Nausea"],
    "Leqembi": ["Micro-Hemorrhage", "Brain Swelling"],
    "Skyrizi": ["Liver enzyme spike", "Fatigue"],
    "Paxlovid": ["Rebound COVID", "Taste loss"],
    "Rinvoq": ["Acne", "Blood Clots"]
}

# In-memory State for Threads
ACTIVE_THREADS = [] # List of {post_id, drug}

def init_files():
    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "drug_name", "pharmacy_id", "quantity_sold", "location"])

    if not os.path.exists(RX_FILE):
        with open(RX_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "drug_name", "doctor_id", "dosage_mg", "patient_age_group"])

    # New Social Schema for Reddit-style feed
    if not os.path.exists(SOCIAL_FILE):
        with open(SOCIAL_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "post_id", "parent_id", "timestamp", "drug_name", "source",
                "author_name", "author_role", "text", 
                "rating", "likes", "shares", "is_launch", "detected_symptom", "location",
                "patient_age", "patient_gender"
            ])

def generate_sales():
    drug = random.choice(DRUGS)
    row = [
        datetime.now().isoformat(),
        drug,
        f"PH-{random.randint(100, 999)}",
        random.randint(1, 50),
        fake.city()
    ]
    with open(SALES_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    print(f"[SALES] {drug} sold.")

def generate_rx():
    drug = random.choice(DRUGS)
    row = [
        datetime.now().isoformat(),
        drug,
        f"DOC-{random.randint(1000, 9999)}",
        random.choice([2, 5, 10, 15]), # Dosage often varied
        random.choice(["18-30", "31-50", "51-70", "71+"])
    ]
    with open(RX_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    print(f"[RX] {drug} prescribed.")

def write_to_csv(row):
    try:
        with open(SOCIAL_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    except Exception as e:
        print(f"Error writing row: {e}")

def create_post(parent_id="", root_drug=None, root_source=None):
    # If parent_id is provided, it's a REPLY. If empty, it's a ROOT.
    is_reply = bool(parent_id)
    
    # 1. SETUP
    if is_reply:
        drug_name = root_drug
        source = root_source
        is_launch_str = "False"
    else:
        drug_name = random.choice(DRUGS)
        source = random.choice(SOURCES)
        is_launch_str = "True"

    # 2. EMERGING SIGNAL (Only for Root posts usually, or if reply mentions it)
    is_emerging = random.random() < 0.3
    detected_symptom = "None"
    if is_emerging:
        detected_symptom = random.choice(EMERGING_SIGNALS.get(drug_name, ["None"]))

    # 3. CONTENT & AUTHOR
    post_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    role = random.choice(ROLES)
    author_name = fake.user_name()
    if role == "Doctor": author_name = f"Dr_{fake.last_name()}"
    elif source == "PubMed": author_name = f"{fake.last_name()}, MD/PhD"; role = "Researcher"

    # Rating Logic: User requested 6,7,8. Avoiding 0s.
    # Emerging signals might still be low rated (safety warning), but we'll keep them > 1
    base_rating = random.randint(6, 10)
    if is_emerging: base_rating = random.randint(2, 6) # Safety issues drop rating
    rating = base_rating

    # TEXT GENERATION
    text = ""
    likes = random.randint(5, 500)
    shares = random.randint(0, 100)

    if is_reply:
        # REPLY TEXT
        if source == "Twitter":
            text = f"@{fake.user_name()} {random.choice(['True!', 'Same here.', 'Fake news.', 'Check DM.', 'OMG yes!', '100% agree'])}"
        elif source == "PubMed":
            text = f"Comment: Methodology seems sound but sample size is small."
            role = "Reviewer"
        else:
            text = f"Replying: {random.choice(['Did u ask ur doc?', 'Thanks for sharing.', 'I had the same issue.', 'Report this to FDA.', 'Great info.'])}"
    else:
        # ROOT TEXT
        if source == "PubMed":
            text = f"Clinical observation: Patient presented with {detected_symptom.lower()} following {drug_name} protocol." if is_emerging else f"Study results: {drug_name} shows efficacy in double-blind trial. No significant adverse events."
            rating = 0 # Scientific papers don't have star ratings usually, but we might want to default to 0 to hidden
        elif source == "Twitter":
            symptom_slang = detected_symptom.lower().replace(" ", "")
            text = f"Has anyone else got #{symptom_slang} from #{drug_name}? 😡" if is_emerging else f"Day 10 on #{drug_name} and feeling amazing! ✨ #healing"
        elif source == "DoctorForum":
            text = f"Noticing a trend of {detected_symptom} in my {drug_name} patients." if is_emerging else f"Prescribing {drug_name} frequently now. Good outcomes."
        else: # Reddit
            if role == "Pharma Rep":
                text = f"📢 OFFICIAL UPDATE: {drug_name} shows superior results. #PharmaLife"
                rating = 10
            else:
                text = f"Is {detected_symptom} normal? on {drug_name}." if is_emerging else f"{drug_name} log. Day 1: Feeling okay."

    # LOCATION (For Badge Batch Analysis)
    location = fake.city()

    # DEMOGRAPHICS (For Advanced RAG)
    patient_age = random.randint(18, 75)
    patient_gender = random.choice(["Male", "Female"])
    
    # Context injection for demographics
    if "women" in text or "under 30" in text:
        patient_gender = "Female"
        patient_age = random.randint(18, 29)

    row = [
        post_id, parent_id, timestamp, drug_name, source,
        author_name, role, text,
        rating, likes, shares, is_launch_str, detected_symptom, location,
        patient_age, patient_gender
    ]
    
    write_to_csv(row)
    return post_id, drug_name, source

def generate_social_burst():
    # 1. Generate ROOT Post
    root_id, root_drug, root_source = create_post(parent_id="")
    print(f"[SOCIAL] NEW THREAD: {root_drug} ({root_source})")
    
    # 2. Generate 2-4 Replies IMMEDIATELY
    num_replies = random.randint(2, 4)
    for _ in range(num_replies):
        create_post(parent_id=root_id, root_drug=root_drug, root_source=root_source)
        
    print(f"      + {num_replies} replies generated.")

if __name__ == "__main__":
    init_files()
    print("Simulating Reddit-style Pharma Feed... Press Ctrl+C to stop.")
    
    # BURST: Generate 20 initial threads (approx 80 posts total)
    print(">>> Generating initial history...")
    for _ in range(20):
        generate_social_burst()
        
    # STREAM: Fast loop
    while True:
        if random.random() < 0.5: generate_sales()
        if random.random() < 0.4: generate_rx()
        generate_social_burst() # Always generate full threads now
        time.sleep(2) # Slower loop because we generate ~4 posts per tick
