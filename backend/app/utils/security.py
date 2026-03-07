"""安全工具"""
import hashlib
import hmac
import time

def verify_slack_signature(signing_secret: str, timestamp: str, body: str, signature: str) -> bool:
    """验证 Slack webhook 签名"""
    if abs(int(timestamp) - int(time.time())) > 60 * 5:
        return False

    sig_basestring = f"v0:{timestamp}:{body}"
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, signature)

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """清理用户输入"""
    if not text:
        return ""
    return text.strip()[:max_length]
