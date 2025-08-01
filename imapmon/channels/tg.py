from click import BadOptionUsage
from bs4 import BeautifulSoup
from imap_tools import MailMessage
#from telegram import Bot, ParseMode
#as per Version 20 you need to use: (https://stackoverflow.com/a/74180161)
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

from imapmon.settings import Settings
from imapmon.channels.base import BaseChannel


class TelegramChannel(BaseChannel):

    def __init__(self, settings: Settings):
        super().__init__(settings)
        assert isinstance(settings.telegram_bot_token, str)
        self.bot = Bot(settings.telegram_bot_token)

    def check_settings(self):
        if not self.settings.telegram_bot_token:
            raise BadOptionUsage(
                'channel',
                'Telegram bot token is required for the Telegram channel'
            )

        if not self.settings.telegram_chat_id:
            raise BadOptionUsage(
                'channel',
                'Telegram Chat ID is required for the Telegram channel'
            )

    @staticmethod
    def clean_string(s: str, max_length: int = 2048):
        s = s.replace('`', "'")
        return s if len(s) <= max_length else s[:max_length] + "..."

    def message(self, msg: MailMessage):
        message_body: str
        if msg.html and len(msg.html) > len(msg.text):
            message_body = BeautifulSoup(msg.html, 'html.parser').get_text('\n', strip=True)
        else:
            message_body = msg.text

        telegram_msg = (
            f'*Mailbox:* `{self.settings.imap_username}`\n'
            f'*From:* `{self.clean_string(msg.from_, 512)}`\n'
            f'*Subject:* `{self.clean_string(msg.subject, 512)}`\n'
            f'*Text:*\n'
            f'```\n{self.clean_string(message_body)}\n```'
        )

        asyncio.run(self.bot.send_message(
            chat_id=self.settings.telegram_chat_id,
            text=telegram_msg,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        ))
