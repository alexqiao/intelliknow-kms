from telegram import Bot

class TelegramClient:
    def __init__(self, token: str):
        self.bot = Bot(token=token)

    async def setup_webhook(self, webhook_url: str):
        await self.bot.set_webhook(url=f"{webhook_url}/webhook/telegram")

    async def send_message(self, chat_id: int, text: str):
        await self.bot.send_message(chat_id=chat_id, text=text)
