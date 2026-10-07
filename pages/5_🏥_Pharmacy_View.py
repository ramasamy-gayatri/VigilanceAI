import streamlit as st
import pandas as pd
import random
import time
import plotly.express as px
import sys
sys.path.append('.')
from utils import load_data

st.set_page_config(page_title="Pharmacy", page_icon="🏥", layout="wide")

st.title("🏥 Pharmacy Command Center")

data = load_data()
sdf = data['social']

# MOCK INVENTORY DATA
drugs = ["Wegovy", "Mounjaro", "Ozempic", "Zepbound", "Skyrizi", "Rinvoq"]
inventory_data = {
    "Wegovy": {"stock": 12, "max": 100, "status": "Low"},
    "Mounjaro": {"stock": 45, "max": 80, "status": "OK"},
    "Ozempic": {"stock": 8, "max": 120, "status": "Critical"},
    "Zepbound": {"stock": 60, "max": 60, "status": "Full"},
    "Skyrizi": {"stock": 25, "max": 40, "status": "OK"},
    "Rinvoq": {"stock": 18, "max": 50, "status": "Low"},
}

col_inv, col_ops = st.columns([1.5, 1])

with col_inv:
    st.markdown("### 📊 Live Inventory & Viral Demand")
    
    try: viral_counts = sdf['drug_name'].value_counts()
    except: viral_counts = pd.Series()

    inv_list = []
    for d in drugs:
        v_score = viral_counts.get(d, random.randint(10, 50))
        stock = inventory_data.get(d, {}).get("stock", 0)
        status = inventory_data.get(d, {}).get("status", "Unknown")
        inv_list.append({"Drug": d, "Viral Velocity": v_score, "Stock Remaining": stock, "Status": status})
        
    df_inv = pd.DataFrame(inv_list)
    
    fig = px.bar(df_inv, x="Drug", y=["Viral Velocity", "Stock Remaining"], barmode="group",
                 color_discrete_map={"Viral Velocity": "#FF4B4B", "Stock Remaining": "#00E5FF"})
    fig.update_layout(paper_bgcolor='#000000', plot_bgcolor='#000000', font=dict(color='white'),
                     title="Demand vs Supply Mismatch", legend_title=None)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### ⚠️ Supply Chain Alerts")
    for index, row in df_inv.iterrows():
        if row['Viral Velocity'] > row['Stock Remaining'] * 2:
             st.error(f"🚨 **High Risk Stockout: {row['Drug']}**")

with col_ops:
    st.markdown("### 📦 Inventory Operations")
    
    st.info("💡 **Smart Restock Recommendation**")
    reorder_list = df_inv[df_inv['Stock Remaining'] < 30]['Drug'].tolist()
    st.write(f"Recommended Orders: {', '.join(reorder_list)}")
    
    st.markdown("---")
    with st.form("restock_form"):
        st.markdown("#### 🚚 Place Wholesale Order")
        drug_order = st.selectbox("Select Drug", drugs)
        qty = st.number_input("Quantity (Units)", min_value=10, value=50, step=10)
        supplier = st.selectbox("Distributor", ["McKesson", "Cardinal Health", "AmerisourceBergen"])
        priority = st.checkbox("Expedited Shipping (+15%)")
        
        submitted = st.form_submit_button("🛒 Book Order")
        if submitted:
            st.success(f"✅ Order #{random.randint(9000,9999)} placed for {qty}x {drug_order} via {supplier}.")
            time.sleep(1)
            st.balloons()
