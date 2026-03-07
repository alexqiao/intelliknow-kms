"""响应格式化工具"""

def format_for_telegram(response: str, intent: str, confidence: float) -> str:
    """格式化 Telegram 消息（支持 Markdown）"""
    header = f"🤖 *Intent: {intent}* (confidence: {confidence:.0%})\n\n"
    return header + response

def format_for_slack(response: str, intent: str, confidence: float) -> str:
    """格式化 Slack 消息（支持 mrkdwn）"""
    header = f"🤖 *Intent: {intent}* (confidence: {confidence:.0%})\n\n"
    return header + response
