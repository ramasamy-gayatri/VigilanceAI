import streamlit as st
import pandas as pd
import sys
sys.path.append('.')
from utils import load_data

st.set_page_config(page_title="Interact (Feed)", page_icon="📱", layout="wide")

st.title("📱 Live Social Stream")

data = load_data()
sdf = data['social']

if sdf.empty:
    st.info("No Data Stream. Run `mock_stream.py`.")
    st.stop()

# --- FILTER ---
filter_option = st.radio("Dataset:", ["All Sources", "Social Media", "Clinical Research (PubMed/DoctorForum)"], horizontal=True)

if filter_option == "Social Media":
    sdf = sdf[sdf['source'].isin(['Reddit', 'Twitter'])]
elif filter_option == "Clinical Research (PubMed/DoctorForum)":
    sdf = sdf[sdf['source'].isin(['PubMed', 'DoctorForum'])]

if sdf.empty:
    st.info("No data for this filter.")
    st.stop()

# --- FEED LOGIC ---
sdf['is_launch'] = sdf['is_launch'].astype(str).replace({'True': True, 'False': False, 'true': True, 'false': False})
sdf['post_id'] = sdf['post_id'].astype(str).str.strip()
sdf['parent_id'] = sdf['parent_id'].fillna("").astype(str).str.strip().replace("nan", "")

parents = sdf[sdf['is_launch'] == True].sort_values('timestamp', ascending=False)
children = sdf[sdf['is_launch'] == False]

if parents.empty and not children.empty:
    parents = children.sort_values('timestamp', ascending=False).head(50)

for _, parent in parents.iterrows():
    thread_comments = children[children['parent_id'] == parent['post_id']]
    score = float(parent['rating']) if not pd.isna(parent['rating']) else 0
    
    border_color = "#2F3336"
    icon = "💬"
    if parent['source'] == "Twitter": border_color = "#1D9BF0"; icon = "🐦"
    elif parent['source'] == "PubMed": border_color = "#2ECC71"; icon = "🔬"
    elif parent['source'] == "DoctorForum": border_color = "#9B59B6"; icon = "🩺"
        
    signal_badge = ""
    if 'detected_symptom' in parent and parent['detected_symptom'] != "None" and pd.notna(parent['detected_symptom']):
        signal_badge = f'<span style="background-color: #330000; color: #FF4B4B; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-left: 10px;">⚠️ DETECTED: {parent["detected_symptom"]}</span>'

    # STRICTLY NO INDENTATION FOR HTML
    st.markdown(f"""
<div style="border-left: 3px solid {border_color}; background-color: #000000; padding: 15px; margin-bottom: 10px; border-bottom: 1px solid #2F3336;">
<div style="display: flex; justify_content: space_between; align-items: center;">
<div>
<span style="font-size: 1.1em; font-weight: bold; color: #E7E9EA;">{parent["author_name"]}</span>
<span style="color: #71767B; font-size: 0.9em; margin-left: 5px;">{icon} {parent["source"]} • {parent["author_role"]}</span>
{signal_badge}
</div>
<span style="color: #71767B; font-size: 0.8em;">{parent["timestamp"]}</span>
</div>
<div style="margin-top: 8px; font-size: 1.05em; color: #E7E9EA; line-height: 1.4;">
{parent["text"]}
</div>
<div style="margin-top: 12px; font-size: 0.9em; color: #71767B; display: flex; gap: 20px;">
<span>❤️ {int(parent["likes"])}</span>
<span>🔄 {int(parent["shares"])}</span>
<span>⭐ {score:.1f}/10</span>
</div>
</div>
""", unsafe_allow_html=True)
        
    with st.expander(f"View {len(thread_comments)} Reviews"):
        for _, child in thread_comments.iterrows():
            role_color = "#64FFDA" if child['author_role'] == 'Doctor' else "#FFB084"
            st.markdown(f"""
<div style="margin-left: 20px; border-left: 2px solid {role_color}; padding-left: 10px; margin-bottom: 8px;">
<strong>{child["author_name"]}</strong> <span style="color: {role_color}; font-size: 0.8em;">{child["author_role"]}</span>
<span style="float: right; color: #8892B0;">Rated: {child["rating"]}/10</span><br>
{child["text"]}
</div>
""", unsafe_allow_html=True)
