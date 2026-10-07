import streamlit as st

st.set_page_config(
    page_title="Vigilance.AI Ecosystem",
    page_icon="🛡️",
    layout="wide"
)

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🛡️ VIGILANCE.AI")
st.subheader("The Operating System for Agentic Pharmacovigilance")

st.markdown("""
### Welcome using the Navigation Sidebar 👈

**Vigilance.AI** unifies live social listening, FDA data, and agentic reasoning into a single platform for:
*   **Pharmaceutical Safety Teams** (Signal Detection)
*   **Doctors** (Pre-Prescription Intelligence)
*   **Pharmacists** (Supply Chain & Inventory)

---
#### System Status
*   **Social Stream**: 🟢 Online
*   **Sales Stream**: 🟢 Online
*   **OpenFDA Link**: 🟢 Connected
*   **Agentic Copilot**: 🟢 Ready (GPT-4o)

*Created by Sanjeev M and Harish Balaji*
""")

st.info("Select a module from the sidebar to begin.")
