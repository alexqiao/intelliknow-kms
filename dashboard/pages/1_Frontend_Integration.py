import streamlit as st
import requests
import os

st.set_page_config(page_title="Frontend Integration", page_icon="🔗")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🔗 Frontend Integration")

tab1, tab2 = st.tabs(["Telegram Bot", "Slack Bot"])

with tab1:
    st.subheader("Telegram Bot Configuration")

    # Load existing config
    try:
        resp = requests.get(f"{BACKEND_URL}/api/config/frontend/telegram")
        existing = resp.json() if resp.status_code == 200 else {}
        creds = existing.get("credentials", {})
    except:
        creds = {}

    telegram_token = st.text_input("Bot Token", value=creds.get("bot_token", ""), type="password", key="telegram_token")
    admin_chat_id = st.text_input("Admin Chat ID (for testing)", value=creds.get("admin_chat_id", ""), key="telegram_chat")
    webhook_url = st.text_input("Webhook URL", value=f"{BACKEND_URL}/webhook/telegram")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save", key="save_telegram"):
            if telegram_token:
                try:
                    resp = requests.post(f"{BACKEND_URL}/api/config/frontend", json={
                        "platform": "telegram",
                        "credentials": {"bot_token": telegram_token, "admin_chat_id": admin_chat_id},
                        "enabled": True
                    })
                    if resp.status_code == 200:
                        st.success("✅ Saved!")
                    else:
                        st.error(f"Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter a token")

    with col2:
        if st.button("Test", key="test_telegram"):
            try:
                resp = requests.post(f"{BACKEND_URL}/api/config/frontend/telegram/test")
                result = resp.json()
                if result.get("ok"):
                    st.success(f"✅ {result.get('message')}")
                else:
                    st.error(f"❌ {result.get('message')}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("""
    **Setup Instructions:**
    1. Open Telegram and search for @BotFather
    2. Send `/newbot` and follow instructions
    3. Copy the Bot Token and paste above
    4. Get your Chat ID by messaging @userinfobot
    5. Set webhook URL in your bot settings
    """)

with tab2:
    st.subheader("Slack Bot Configuration")

    # Load existing config
    try:
        resp = requests.get(f"{BACKEND_URL}/api/config/frontend/slack")
        existing = resp.json() if resp.status_code == 200 else {}
        creds = existing.get("credentials", {})
    except:
        creds = {}

    slack_token = st.text_input("Bot Token", value=creds.get("bot_token", ""), type="password", key="slack_token")
    slack_secret = st.text_input("Signing Secret", value=creds.get("signing_secret", ""), type="password", key="slack_secret")
    admin_channel = st.text_input("Admin Channel ID (for testing)", value=creds.get("admin_channel", ""), key="slack_channel")
    webhook_url_slack = st.text_input("Webhook URL", value=f"{BACKEND_URL}/webhook/slack")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save", key="save_slack"):
            if slack_token and slack_secret:
                try:
                    resp = requests.post(f"{BACKEND_URL}/api/config/frontend", json={
                        "platform": "slack",
                        "credentials": {"bot_token": slack_token, "signing_secret": slack_secret, "admin_channel": admin_channel},
                        "enabled": True
                    })
                    if resp.status_code == 200:
                        st.success("✅ Saved!")
                    else:
                        st.error(f"Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter valid credentials")

    with col2:
        if st.button("Test", key="test_slack"):
            try:
                resp = requests.post(f"{BACKEND_URL}/api/config/frontend/slack/test")
                result = resp.json()
                if result.get("ok"):
                    st.success(f"✅ {result.get('message')}")
                else:
                    st.error(f"❌ {result.get('message')}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("""
    **Setup Instructions:**
    1. Visit https://api.slack.com/apps
    2. Create a new app
    3. Enable Event Subscriptions
    4. Subscribe to `message.channels` event
    5. Copy Bot Token and Signing Secret
    """)
