from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

class SlackClient:
    def __init__(self, token: str, signing_secret: str):
        self.client = WebClient(token=token)
        self.verifier = SignatureVerifier(signing_secret)

    async def send_message(self, channel: str, text: str):
        self.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        )

    def verify_request(self, timestamp: str, signature: str, body: str) -> bool:
        return self.verifier.is_valid(body, timestamp, signature)
