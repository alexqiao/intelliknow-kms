"""响应格式化工具"""
import re

def format_for_telegram(response: str, intent: str, confidence: float) -> str:
    """格式化 Telegram 消息（转换为纯文本）"""
    # Convert markdown to plain text
    text = response.replace('**', '')  # Remove bold markers
    text = re.sub(r'^- ', '• ', text, flags=re.MULTILINE)  # Convert bullet points

    header = f"🤖 Intent: {intent} (confidence: {confidence:.0%})\n\n"
    return header + text

def format_for_slack(response: str, intent: str, confidence: float) -> str:
    """格式化 Slack 消息（支持 mrkdwn）"""
    header = f"🤖 *Intent: {intent}* (confidence: {confidence:.0%})\n\n"
    return header + response
