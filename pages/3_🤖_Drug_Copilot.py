import streamlit as st
import sys
sys.path.append('.')
from utils import query_copilot

st.set_page_config(page_title="Copilot", page_icon="🤖", layout="wide")

st.title("🤖 Agentic Copilot")
st.info("Answers grounded in Live Social/Clinical Stream (RAG) + FDA Labels.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask about drug safety (e.g. 'Side effects of Wegovy for women under 30')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.spinner("Consulting live knowledge base..."):
        response_text = query_copilot(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.write(response_text)
