import streamlit as st
import requests
import os

st.set_page_config(page_title="Knowledge Base", page_icon="📚")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

st.title("📚 Knowledge Base Management")

st.subheader("Upload Document")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

# Get available intents
try:
    intents_response = requests.get(f"{BACKEND_URL}/api/intents")
    if intents_response.status_code == 200:
        intents = intents_response.json()
        intent_options = {i["name"]: i["id"] for i in intents}
        intent_selection = st.multiselect("Assign to Intents", list(intent_options.keys()))
    else:
        intent_selection = []
        st.warning("Could not load intents")
except:
    intent_selection = []
    st.warning("Backend not available")

if st.button("Upload") and uploaded_file:
    files = {"file": uploaded_file}
    data = {}
    if intent_selection:
        intent_ids = ",".join([str(intent_options[name]) for name in intent_selection])
        data["intent_ids"] = intent_ids

    try:
        response = requests.post(f"{BACKEND_URL}/api/documents/upload", files=files, data=data)
        if response.status_code == 200:
            st.success(f"✅ Document uploaded: {uploaded_file.name}")
            st.rerun()
        else:
            st.error(f"Upload failed: {response.text}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.subheader("Document Library")

try:
    response = requests.get(f"{BACKEND_URL}/api/documents")
    if response.status_code == 200:
        docs = response.json()
        if docs:
            for doc in docs:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.text(f"📄 {doc['filename']}")
                with col2:
                    st.text(f"Size: {format_file_size(doc.get('file_size', 0))}")
                with col3:
                    st.text(f"Chunks: {doc['chunk_count']}")
                with col4:
                    if st.button("Delete", key=f"del_{doc['id']}"):
                        try:
                            resp = requests.delete(f"{BACKEND_URL}/api/documents/{doc['id']}")
                            if resp.status_code == 200:
                                st.success("Document deleted")
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {resp.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.info("No documents uploaded yet")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.warning("Backend not available")
