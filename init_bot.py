import os
import logging

from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher

logging.basicConfig(level=logging.INFO)
load_dotenv(find_dotenv())

# лучше поднять таймаут до 2-х мин
session = AiohttpSession(timeout=120.0)

bot: Bot = Bot(os.getenv('BOT_TOKEN'),
               parse_mode='html',
               session=session)

dp: Dispatcher = Dispatcher()

