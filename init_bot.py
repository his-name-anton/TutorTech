import os
import logging
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher

logging.basicConfig(level=logging.INFO)


load_dotenv(find_dotenv())
bot: Bot = Bot(os.getenv('BOT_TOKEN'), parse_mode='html')
dp: Dispatcher = Dispatcher()