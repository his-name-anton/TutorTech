import os
import asyncio
import logging
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher

from menu import menu_router

logging.basicConfig(level=logging.INFO)


load_dotenv(find_dotenv())
bot: Bot = Bot(os.getenv('BOT_TOKEN'))
dp: Dispatcher = Dispatcher()


# MAIN MENU
dp.include_router(menu_router.router)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        print(KeyboardInterrupt)