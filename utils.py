import streamlit as st
from openai import OpenAI
import pandas as pd
import os
import requests
import json
from dotenv import load_dotenv
import fetch_fda 

load_dotenv()

# --- SHARED FUNCTIONS ---

def load_data():
    """Robust data loader with empty fallback"""
    data = {}
    try: data['social'] = pd.read_csv("./data/social_stream.csv")
    except: data['social'] = pd.DataFrame()
    
    try: data['rx'] = pd.read_csv("./data/prescriptions_stream.csv")
    except: data['rx'] = pd.DataFrame()
    
    try: data['sales'] = pd.read_csv("./data/sales_stream.csv")
    except: data['sales'] = pd.DataFrame()
    return data

def query_copilot(user_query):
    """
    Hybrid RAG Logic for Drug Copilot
    """
    client = OpenAI()
    
    # 1. IDENTIFY DRUG
    target_drug = "Unknown"
    for drug in ["Wegovy", "Leqembi", "Mounjaro", "Skyrizi", "Paxlovid", "Rinvoq", "Ozempic"]:
        if drug.lower() in user_query.lower():
            target_drug = drug
            break
            
    # 2. FDA CONTEXT
    fda_context = ""
    if target_drug != "Unknown":
        try:
            label = fetch_fda.fetch_drug_label(target_drug)
            if label:
                fda_context = f"FDA LABEL FOR {target_drug}: {label.get('warnings', '')[:1000]}..."
        except: pass
        
    # 3. SOCIAL CONTEXT (Hybrid RAG)
    social_insight = "No live social data available."
    try:
        sdf = pd.read_csv("./data/social_stream.csv")
        
        # Demographic Filtering
        filtered_sdf = sdf.copy()
        filter_desc = "All Patients"
        
        # Gender
        if "women" in user_query.lower() or "female" in user_query.lower():
            filtered_sdf = filtered_sdf[filtered_sdf['patient_gender'] == "Female"]; filter_desc += ", Female"
        elif "men" in user_query.lower() or "male" in user_query.lower():
            filtered_sdf = filtered_sdf[filtered_sdf['patient_gender'] == "Male"]; filter_desc += ", Male"
            
        # Age
        if "under 30" in user_query.lower():
            filtered_sdf = filtered_sdf[filtered_sdf['patient_age'] < 30]; filter_desc += ", <30 years"
        elif "over 50" in user_query.lower():
            filtered_sdf = filtered_sdf[filtered_sdf['patient_age'] > 50]; filter_desc += ", >50 years"
            
        # Drug Filter
        if target_drug != "Unknown":
            filtered_sdf = filtered_sdf[filtered_sdf['drug_name'] == target_drug]
            
        # Calc Stats
        if not filtered_sdf.empty:
            symptoms = filtered_sdf[filtered_sdf['detected_symptom'] != "None"]['detected_symptom'].value_counts().head(3).to_dict()
            total_reports = len(filtered_sdf)
            avg_rating = filtered_sdf['rating'].mean()
            
            social_insight = f"""
            LIVE OBSERVATIONAL DATA ({filter_desc}):
            - Sample Size: {total_reports} reports filtered.
            - Drug: {target_drug}
            - Top Side Effects: {symptoms}
            - Avg Satisfaction: {avg_rating:.1f}/10
            """
        else:
            social_insight = f"No reports found matching criteria: {filter_desc}"
            
    except Exception as e:
        social_insight = f"Social Analytics Error: {e}"

    # 4. LLM CALL
    full_prompt = f"""
    You are Vigilance.AI, a specialized safety analyst.
    USER QUERY: "{user_query}"
    SOURCE 1 (FDA): {fda_context}
    SOURCE 2 (LIVE SOCIAL): {social_insight}
    
    INSTRUCTIONS:
    1. Prioritize LIVE SOCIAL DATA for specific groups (e.g. "women under 30").
    2. Highlight discrepancies between FDA labels and Live Signals.
    3. Format as "Clinical Insight".
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"**Analysis based on Live Stream:** \n\n{social_insight}\n\n*(AI Generation Unavailable: {e})*"
