import logging
import sys
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from check import check_droplet_connectivity, change_ip
from dotenv import get_key
import json


class TelegramPrintHandler:
    def __init__(self, bot, chat_ids):
        self.bot = bot
        self.chat_ids = chat_ids

    def write(self, message):
        if message.strip():  # To avoid sending empty lines
            for chat_id in self.chat_ids:
                asyncio.run(self.bot.send_message(chat_id=chat_id, text=message.strip()))

    def flush(self):
        pass

chat_id = get_key(".env","chat_id")
droplets = []
API_TOKEN = get_key(".env","wh_bot_token")
ADMINS = get_key(".env",'wh_bot_admins').split(',')


domain_cheatsheet = json.loads(get_key(".env","domain_cheatsheet"))
for dro, subdo in domain_cheatsheet.items():
    droplets.append(dro)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

BUSY=False

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        for droplet in droplets:
            kb.row(KeyboardButton(f"Check {droplet}"),KeyboardButton(f"Change {droplet}"))
        await message.reply("Hello! Welcome to the bot.\nChoose an option:",reply_markup=kb)
    else: await message.reply("Go away!")




@dp.message_handler(lambda message: True)
async def handle_message(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        global BUSY
        if not BUSY:
            for droplet in droplets:
                if droplet in message.text and message.text.startswith("Check"):
                    await message.reply(f"Checking connectivity of {droplet}...")
                    BUSY = True
                    res = str(check_droplet_connectivity(droplet))
                    await message.reply(f"Connectivity of {droplet} is {res}%")
                    BUSY = False
                elif droplet in message.text and message.text.startswith("Change"):
                    await message.reply(f"Changing {droplet} IP...")
                    BUSY = True
                    new_IP,subdomain = change_ip(droplet)
                    await message.reply(f"{droplet} IP changed to {new_IP} and set to {subdomain}.shaxerver.online")
                    BUSY = False
            return
        else: await message.reply("Server is busy...")
    else: await message.reply("Go away!")


if __name__ == '__main__':
    print('Starting server...')
    executor.start_polling(dp, skip_updates=True)