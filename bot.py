import asyncio
from init_bot import bot, dp
from menu import menu_router
from handlers.roudmap import road_map
from handlers.quizzes import quiz

dp.include_router(road_map.router)
dp.include_router(quiz.router)
dp.include_router(menu_router.router)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        print(KeyboardInterrupt)