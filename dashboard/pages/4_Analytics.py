import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from io import StringIO

st.set_page_config(page_title="Analytics", page_icon="📊")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("📊 Analytics Dashboard")

try:
    response = requests.get(f"{BACKEND_URL}/api/analytics")
    if response.status_code == 200:
        data = response.json()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Queries", data.get("total_queries", 0))
        with col2:
            st.metric("Avg Response Time", f"{data.get('avg_response_time', 0):.0f} ms")
        with col3:
            st.metric("Active Intents", len(data.get("by_intent", {})))

        st.markdown("---")

        # CSV Export
        try:
            logs_resp = requests.get(f"{BACKEND_URL}/api/query_logs")
            if logs_resp.status_code == 200:
                logs_data = logs_resp.json()
                if logs_data:
                    df_logs = pd.DataFrame(logs_data)
                    csv = df_logs.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Query Logs (CSV)",
                        data=csv,
                        file_name="query_logs.csv",
                        mime="text/csv"
                    )
        except:
            pass

        st.markdown("---")

        if data.get("total_queries", 0) > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Query Distribution by Intent")
                intent_data = data.get("by_intent", {})
                if intent_data:
                    df = pd.DataFrame(list(intent_data.items()), columns=["Intent", "Count"])
                    fig = px.pie(df, values="Count", names="Intent")
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Most Accessed Documents")
                try:
                    docs_resp = requests.get(f"{BACKEND_URL}/api/documents")
                    if docs_resp.status_code == 200:
                        docs = docs_resp.json()
                        if docs:
                            df_docs = pd.DataFrame(docs)
                            df_docs = df_docs.sort_values("access_count", ascending=False).head(5)
                            st.dataframe(df_docs[["filename", "access_count"]], use_container_width=True)
                        else:
                            st.info("No documents available")
                except:
                    st.info("Document stats coming soon")
        else:
            st.info("No query data available yet")

except:
    st.warning("Backend not available")
