"""响应格式化工具"""
import re

def escape_markdown(text: str) -> str:
    """转义Telegram Markdown特殊字符"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def format_for_telegram(response: str, intent: str, confidence: float) -> str:
    """格式化 Telegram 消息（支持 Markdown）"""
    header = f"🤖 *Intent: {intent}* (confidence: {confidence:.0%})\n\n"
    escaped_response = escape_markdown(response)
    return header + escaped_response

def format_for_slack(response: str, intent: str, confidence: float) -> str:
    """格式化 Slack 消息（支持 mrkdwn）"""
    header = f"🤖 *Intent: {intent}* (confidence: {confidence:.0%})\n\n"
    return header + response
