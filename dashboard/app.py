import streamlit as st
import requests
import os

st.set_page_config(page_title="IntelliKnow KMS", page_icon="🧠", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🧠 IntelliKnow KMS")
st.markdown("### Knowledge Management System powered by Gen AI")

col1, col2, col3 = st.columns(3)

try:
    docs_resp = requests.get(f"{BACKEND_URL}/api/documents")
    analytics_resp = requests.get(f"{BACKEND_URL}/api/analytics")
    intents_resp = requests.get(f"{BACKEND_URL}/api/intents")

    doc_count = len(docs_resp.json()) if docs_resp.status_code == 200 else 0
    query_count = analytics_resp.json().get("total_queries", 0) if analytics_resp.status_code == 200 else 0
    intent_count = len(intents_resp.json()) if intents_resp.status_code == 200 else 0

    with col1:
        st.metric("Total Documents", doc_count)
    with col2:
        st.metric("Total Queries", query_count)
    with col3:
        st.metric("Active Intents", intent_count)
except:
    with col1:
        st.metric("Total Documents", "N/A")
    with col2:
        st.metric("Total Queries", "N/A")
    with col3:
        st.metric("Active Intents", "N/A")

st.markdown("---")

st.markdown("""
### Quick Start
1. **Frontend Integration** - Configure Telegram/Slack bots
2. **Knowledge Base** - Upload documents (PDF, DOCX)
3. **Intent Config** - Manage intent categories
4. **Analytics** - View query statistics
""")

st.info("Navigate using the sidebar to access different features.")
