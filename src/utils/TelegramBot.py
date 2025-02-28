from telegram import Bot
from config import *

async def send_message(message):
    bot = Bot(token=TOKEN_TG)
    await bot.send_message(chat_id=CHAT_ID, text=message)
