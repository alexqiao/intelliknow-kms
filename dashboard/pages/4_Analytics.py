import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Analytics", page_icon="📊")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("📊 Analytics Dashboard")

try:
    response = requests.get(f"{BACKEND_URL}/api/analytics")
    if response.status_code == 200:
        data = response.json()

        # Load query logs for detailed analytics
        logs_data = []
        try:
            logs_resp = requests.get(f"{BACKEND_URL}/api/query_logs")
            if logs_resp.status_code == 200:
                logs_data = logs_resp.json()
        except:
            pass

        # Calculate response time stats
        avg_rt = data.get('avg_response_time', 0)
        rt_status = "Normal" if avg_rt <= 3000 else "Slow"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Queries", data.get("total_queries", 0))
        with col2:
            st.metric("Avg Response Time", f"{avg_rt:.0f} ms",
                       delta=f"{'OK' if avg_rt <= 3000 else 'SLOW'}")
        with col3:
            st.metric("Active Intents", len(data.get("by_intent", {})))
        with col4:
            if logs_data:
                high_conf = sum(1 for l in logs_data if l.get("confidence_score", 0) > 0.7)
                accuracy = (high_conf / len(logs_data)) * 100 if logs_data else 0
                st.metric("Classification Accuracy", f"{accuracy:.0f}%")
            else:
                st.metric("Classification Accuracy", "N/A")

        st.markdown("---")

        # Response Time Alert
        if avg_rt > 3000:
            st.error(f"Average response time ({avg_rt:.0f}ms) exceeds 3000ms target. Consider optimizing the query pipeline.")

        # CSV Export
        if logs_data:
            df_logs = pd.DataFrame(logs_data)
            csv = df_logs.to_csv(index=False)
            st.download_button(
                label="📥 Download Query Logs (CSV)",
                data=csv,
                file_name="query_logs.csv",
                mime="text/csv"
            )

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

            # Response Time Distribution
            if logs_data:
                st.markdown("---")
                st.subheader("Response Time Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    # Response time distribution histogram
                    rt_values = [l.get("response_time_ms", 0) for l in logs_data if l.get("response_time_ms")]
                    if rt_values:
                        df_rt = pd.DataFrame({"Response Time (ms)": rt_values})
                        fig_rt = px.histogram(
                            df_rt,
                            x="Response Time (ms)",
                            nbins=20,
                            title="Response Time Distribution",
                            color_discrete_sequence=["#636EFA"]
                        )
                        fig_rt.add_vline(x=3000, line_dash="dash", line_color="red",
                                         annotation_text="3s Target")
                        st.plotly_chart(fig_rt, use_container_width=True)

                with col2:
                    # Response time stats
                    if rt_values:
                        st.markdown("**Response Time Statistics**")
                        st.write(f"- Min: **{min(rt_values)} ms**")
                        st.write(f"- Max: **{max(rt_values)} ms**")
                        st.write(f"- Average: **{sum(rt_values) / len(rt_values):.0f} ms**")
                        median = sorted(rt_values)[len(rt_values) // 2]
                        st.write(f"- Median: **{median} ms**")
                        within_target = sum(1 for v in rt_values if v <= 3000)
                        pct = (within_target / len(rt_values)) * 100
                        st.write(f"- Within 3s target: **{pct:.0f}%** ({within_target}/{len(rt_values)})")

                        if pct < 90:
                            st.warning(f"Only {pct:.0f}% of queries meet the 3-second target.")
                        else:
                            st.success(f"{pct:.0f}% of queries meet the 3-second target.")

                # Response time by frontend source
                st.markdown("---")
                st.subheader("Performance by Frontend Source")
                sources = {}
                for l in logs_data:
                    src = l.get("frontend_source", "unknown")
                    if src not in sources:
                        sources[src] = []
                    if l.get("response_time_ms"):
                        sources[src].append(l["response_time_ms"])

                if sources:
                    source_stats = []
                    for src, times in sources.items():
                        if times:
                            source_stats.append({
                                "Source": src,
                                "Queries": len(times),
                                "Avg RT (ms)": int(sum(times) / len(times)),
                                "Max RT (ms)": max(times),
                                "Within 3s": f"{sum(1 for t in times if t <= 3000) / len(times) * 100:.0f}%"
                            })
                    if source_stats:
                        st.dataframe(pd.DataFrame(source_stats), use_container_width=True)

        else:
            st.info("No query data available yet. Send queries via Telegram or Slack to see analytics.")

except Exception as e:
    st.error(f"Error loading analytics: {str(e)}")
    st.warning("Backend not available")
