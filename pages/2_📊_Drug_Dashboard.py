import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.append('.')
from utils import load_data

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Pharmacovigilance Command Center")

data = load_data()
social = data['social']
rx = data['rx']

if social.empty:
    st.error("Waiting for data pipelines...")
    st.stop()

# --- KPIS ---
col1, col2, col3, col4 = st.columns(4)
total_ae = len(social[social['author_role'] == 'Patient'])
avg_rating = social[social['rating'] > 0]['rating'].mean()
risk_score = (total_ae * 1.5) / (len(rx) + 1) * 100 

with col1: st.metric("Active Prescriptions", f"{len(rx)}")
with col2: st.metric("Safety Events", f"{total_ae}")
with col3: st.metric("Avg Sentiment", f"{avg_rating:.1f}/10")
with col4: st.metric("Risk Index", f"{risk_score:.1f}")

st.markdown("---")

# --- CHARTS ---
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 📈 Safety Signal Trend")
    if not social.empty:
        social['ts'] = pd.to_datetime(social['timestamp'])
        ae_trend = social[social['author_role'] == 'Patient'].set_index('ts').resample('1min')['post_id'].count().reset_index()
        fig = px.area(ae_trend, x='ts', y='post_id', title=None, color_discrete_sequence=['#F4212E'])
        fig.update_layout(paper_bgcolor='#000000', plot_bgcolor='#000000', font=dict(color='#71767B'))
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### 💊 Rx Share")
    if not rx.empty:
        dist = rx['drug_name'].value_counts().reset_index()
        dist.columns = ['Drug', 'Count']
        fig2 = px.pie(dist, values='Count', names='Drug', hole=0.6, color_discrete_sequence=px.colors.qualitative.Dark24)
        fig2.update_layout(paper_bgcolor='#000000', font=dict(color='white'), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Clinical Deep-Dive")

r3_1, r3_2 = st.columns([1, 1])

with r3_1:
    st.markdown("#### Adverse Event Frequency")
    symptom_data = social[(social['detected_symptom'].notna()) & (social['detected_symptom'] != "None")]
    if not symptom_data.empty:
        symptom_counts = symptom_data['detected_symptom'].value_counts().reset_index()
        symptom_counts.columns = ['Symptom', 'Count']
        fig_symptom = px.bar(symptom_counts, x='Count', y='Symptom', orientation='h', 
                            color='Count', color_continuous_scale='Reds', template='plotly_dark')
        st.plotly_chart(fig_symptom, use_container_width=True)
    else: st.info("No Data")

with r3_2:
    st.markdown("#### Doctor vs Patient Sentiment")
    social['time_short'] = pd.to_datetime(social['timestamp']).dt.strftime('%H:%M')
    if 'rating' in social.columns:
        sentiment = social.groupby(['time_short', 'author_role'])['rating'].mean().reset_index()
        fig_sent = px.line(sentiment, x='time_short', y='rating', color='author_role', 
                        color_discrete_map={"Doctor": "#00E5FF", "Patient": "#FF4081"}, markers=True, template='plotly_dark')
        st.plotly_chart(fig_sent, use_container_width=True)
