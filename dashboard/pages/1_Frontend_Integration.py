import streamlit as st
import requests
import os

st.set_page_config(page_title="Frontend Integration", page_icon="🔗")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def mask_credential(value):
    """Show only last 4 characters of a credential"""
    if not value or len(value) < 8:
        return value
    return "****" + value[-4:]

st.title("🔗 Frontend Integration")

tab1, tab2 = st.tabs(["Telegram Bot", "Slack Bot"])

with tab1:
    st.subheader("Telegram Bot Configuration")

    # Load existing config
    existing_telegram = {}
    telegram_creds = {}
    telegram_status = "Disconnected"
    try:
        resp = requests.get(f"{BACKEND_URL}/api/config/frontend/telegram")
        if resp.status_code == 200:
            existing_telegram = resp.json()
            telegram_creds = existing_telegram.get("credentials", {})
            if existing_telegram.get("enabled") and telegram_creds.get("bot_token"):
                telegram_status = "Connected"
    except:
        pass

    # Status indicator
    if telegram_status == "Connected":
        st.success(f"Status: {telegram_status}")
        st.caption(f"Bot Token: {mask_credential(telegram_creds.get('bot_token', ''))}")
        st.caption(f"Admin Chat ID: {telegram_creds.get('admin_chat_id', 'Not set')}")
    else:
        st.warning(f"Status: {telegram_status}")

    st.markdown("---")

    with st.expander("Update Configuration", expanded=(telegram_status == "Disconnected")):
        telegram_token = st.text_input("Bot Token", value="", type="password", key="telegram_token",
                                       placeholder="Enter new token or leave blank to keep current")
        admin_chat_id = st.text_input("Admin Chat ID (for testing)",
                                      value=telegram_creds.get("admin_chat_id", ""), key="telegram_chat")
        webhook_url = st.text_input("Webhook URL", value=f"{BACKEND_URL}/webhook/telegram")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", key="save_telegram"):
                token_to_save = telegram_token if telegram_token else telegram_creds.get("bot_token", "")
                if token_to_save:
                    try:
                        resp = requests.post(f"{BACKEND_URL}/api/config/frontend", json={
                            "platform": "telegram",
                            "credentials": {"bot_token": token_to_save, "admin_chat_id": admin_chat_id},
                            "enabled": True
                        })
                        if resp.status_code == 200:
                            st.success("✅ Saved!")
                            st.rerun()
                        else:
                            st.error(f"Failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter a token")

        with col2:
            if st.button("Test Connection", key="test_telegram"):
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
    existing_slack = {}
    slack_creds = {}
    slack_status = "Disconnected"
    try:
        resp = requests.get(f"{BACKEND_URL}/api/config/frontend/slack")
        if resp.status_code == 200:
            existing_slack = resp.json()
            slack_creds = existing_slack.get("credentials", {})
            if existing_slack.get("enabled") and slack_creds.get("bot_token"):
                slack_status = "Connected"
    except:
        pass

    # Status indicator
    if slack_status == "Connected":
        st.success(f"Status: {slack_status}")
        st.caption(f"Bot Token: {mask_credential(slack_creds.get('bot_token', ''))}")
        st.caption(f"Signing Secret: {mask_credential(slack_creds.get('signing_secret', ''))}")
        st.caption(f"Admin Channel: {slack_creds.get('admin_channel', 'Not set')}")
    else:
        st.warning(f"Status: {slack_status}")

    st.markdown("---")

    with st.expander("Update Configuration", expanded=(slack_status == "Disconnected")):
        slack_token = st.text_input("Bot Token", value="", type="password", key="slack_token",
                                    placeholder="Enter new token or leave blank to keep current")
        slack_secret = st.text_input("Signing Secret", value="", type="password", key="slack_secret",
                                     placeholder="Enter new secret or leave blank to keep current")
        admin_channel = st.text_input("Admin Channel ID (for testing)",
                                      value=slack_creds.get("admin_channel", ""), key="slack_channel")
        webhook_url_slack = st.text_input("Webhook URL", value=f"{BACKEND_URL}/webhook/slack")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", key="save_slack"):
                token_to_save = slack_token if slack_token else slack_creds.get("bot_token", "")
                secret_to_save = slack_secret if slack_secret else slack_creds.get("signing_secret", "")
                if token_to_save and secret_to_save:
                    try:
                        resp = requests.post(f"{BACKEND_URL}/api/config/frontend", json={
                            "platform": "slack",
                            "credentials": {
                                "bot_token": token_to_save,
                                "signing_secret": secret_to_save,
                                "admin_channel": admin_channel
                            },
                            "enabled": True
                        })
                        if resp.status_code == 200:
                            st.success("✅ Saved!")
                            st.rerun()
                        else:
                            st.error(f"Failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter valid credentials")

        with col2:
            if st.button("Test Connection", key="test_slack"):
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
