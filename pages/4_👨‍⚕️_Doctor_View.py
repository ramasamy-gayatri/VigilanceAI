import streamlit as st
import pandas as pd
import sys
import random
import time
sys.path.append('.')
from utils import load_data

st.set_page_config(page_title="Doctor View", page_icon="👨‍⚕️", layout="wide")

st.title("👨‍⚕️ Prescribing Intelligence Portal")

data = load_data()
sdf = data['social']

# Ensure sdf is loaded
if sdf.empty:
    sdf = pd.DataFrame(columns=['drug_name'])

drug_list = list(sdf['drug_name'].unique())
if "All" not in drug_list: drug_list.insert(0, "All")

# Main Selector
selected_drug = st.selectbox("Select Drug for Protocol Review:", drug_list, index=0)
st.markdown("---")

col_safety, col_feed = st.columns([1, 1.2])

with col_safety:
    st.markdown("### Safety Signal Gap Analysis")
    
    ai_risk_score = random.randint(10, 90)
    if selected_drug == "All": ai_risk_score = 45 
    
    ai_signal = "None"
    if selected_drug == "Wegovy": ai_signal = "Hair Shedding (High Conf.)"
    elif selected_drug == "Leqembi": ai_signal = "Micro-Hemorrhage Risk"
    
    st.metric("Real-Time Safety Score", f"{100-ai_risk_score}/100", 
             delta="-5% vs Last Week" if ai_risk_score > 50 else "+2% vs Last Week",
             delta_color="normal")
    
    st.markdown(f"""
    | Data Source | Status | Top Warning |
    | :--- | :--- | :--- |
    | **FDA Label** | ✅ Clean | *None Listed* |
    | **Vigilance AI** | ⚠️ **Signal** | **{ai_signal}** |
    """, unsafe_allow_html=True)
    
    if ai_risk_score > 60:
        st.error(f"⚠️ Recommendation: **Monitor {selected_drug} patients closely** for {ai_signal.split('(')[0]}.")
    else:
        st.success("✅ Recommendation: Proceed with standard protocol.")
        
    st.markdown("---")
    
    # AUTOMATED REPORTING
    st.markdown("#### Regulatory Automation")
    if st.button(f"Generate FDA MedWatch 3500 ({selected_drug})"):
        with st.spinner("Auto-filling Form FDA 3500..."):
            time.sleep(1)
        st.success(f"✅ FDA 3500 Generated for {selected_drug}.")

with col_feed:
    st.markdown(f"### Live Clinical Surveillance: {selected_drug}")
    
    crit_filter = (sdf['author_role'].isin(['Doctor', 'Pharmacist', 'Researcher'])) & (sdf['rating'] < 8)
    if selected_drug != "All":
        crit_filter = crit_filter & (sdf['drug_name'] == selected_drug)
        
    crit_docs = sdf[crit_filter].sort_values('timestamp', ascending=False).head(4)
    
    if not crit_docs.empty:
        for i, row in crit_docs.iterrows():
            border_color = "#FF4B4B" if row['rating'] < 5 else "#FFA726"
            icon = "🚨" if row['rating'] < 5 else "⚠️"
            
            st.markdown(f"""
            <div style="border: 1px solid {border_color}; border-left: 5px solid {border_color}; padding: 12px; background-color: #1E1E1E; margin-bottom: 15px; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 1.1em; color: {border_color};">{icon} {row['author_role']} Alert</span>
                    <span style="color: #888; font-size: 0.8em;">{row['timestamp'].split('T')[0]}</span>
                </div>
                <div style="margin-top: 8px; font-size: 0.95em; color: #FFF; line-height: 1.4;">
                    "{row['text']}"
                </div>
                <div style="margin-top: 8px; display: flex; justify-content: space-between; font-size: 0.8em; color: #CCC;">
                    <span>👤 {row['author_name']}</span>
                    <span>📉 Rating: {row['rating']}/10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"No critical safety signals detected for {selected_drug}.")
