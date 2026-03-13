import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Intent Config", page_icon="🎯")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🎯 Intent Configuration")

st.subheader("Create New Intent")

with st.form("new_intent"):
    name = st.text_input("Intent Name")
    description = st.text_area("Description")
    keywords = st.text_input("Keywords (comma-separated)")

    if st.form_submit_button("Create Intent"):
        if name and description:
            try:
                response = requests.post(f"{BACKEND_URL}/api/intents", json={
                    "name": name,
                    "description": description,
                    "keywords": keywords
                })
                if response.status_code == 200:
                    st.success(f"✅ Intent '{name}' created")
                    st.rerun()
                else:
                    st.error(f"Failed to create intent: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error("Cannot connect to backend")

st.markdown("---")
st.subheader("Existing Intents")

try:
    response = requests.get(f"{BACKEND_URL}/api/intents")
    if response.status_code == 200:
        intents = response.json()

        # Get query logs (with separate error handling)
        logs = []
        try:
            logs_resp = requests.get(f"{BACKEND_URL}/api/query_logs")
            if logs_resp.status_code == 200:
                logs = logs_resp.json()
        except:
            pass

        for intent in intents:
            with st.expander(f"🎯 {intent['name']}"):
                # Filter logs for this intent
                intent_logs = [l for l in logs if l.get("classified_intent") == intent["name"]]

                # Calculate accuracy
                if intent_logs:
                    accurate = sum(1 for l in intent_logs if l.get("confidence_score", 0) > 0.8)
                    accuracy = (accurate / len(intent_logs)) * 100
                    st.metric("Classification Accuracy Rate", f"{accuracy:.1f}%")

                st.write(f"**Description:** {intent['description']}")
                st.write(f"**Keywords:** {intent['keywords']}")

                # Query Classification Log
                if intent_logs:
                    st.markdown("**Recent Queries:**")
                    try:
                        df_logs = pd.DataFrame(intent_logs)
                        if not df_logs.empty and all(col in df_logs.columns for col in ["query_text", "confidence_score", "timestamp"]):
                            df_logs = df_logs[["query_text", "confidence_score", "timestamp"]].head(10)
                            st.dataframe(df_logs, use_container_width=True)
                    except Exception as e:
                        st.info(f"No query data to display")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit", key=f"edit_{intent['id']}"):
                        st.session_state[f"editing_{intent['id']}"] = True
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"del_{intent['id']}"):
                        requests.delete(f"{BACKEND_URL}/api/intents/{intent['id']}")
                        st.rerun()

                if st.session_state.get(f"editing_{intent['id']}", False):
                    with st.form(f"edit_form_{intent['id']}"):
                        new_name = st.text_input("Name", value=intent['name'])
                        new_desc = st.text_area("Description", value=intent['description'])
                        new_keywords = st.text_input("Keywords", value=intent['keywords'])

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Save"):
                                try:
                                    response = requests.put(f"{BACKEND_URL}/api/intents/{intent['id']}", json={
                                        "name": new_name,
                                        "description": new_desc,
                                        "keywords": new_keywords
                                    })
                                    if response.status_code == 200:
                                        st.session_state[f"editing_{intent['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to update intent: {response.text}")
                                except requests.exceptions.RequestException as e:
                                    st.error("Cannot connect to backend")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"editing_{intent['id']}"] = False
                                st.rerun()
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.warning("Backend not available")
