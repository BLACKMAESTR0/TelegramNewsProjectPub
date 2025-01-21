import os
import asyncio
import logging
import signal

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.models import async_main
import app.database.request as rq
from app.middlewares.middleware_check_user import CheckUserMiddleware
from app.middlewares.middleware_hello import HelloMiddleware
from app.notifications import start_scheduler

signality = None

def signal_handler(signal, frame):
    signality.cancel()
    asyncio.get_running_loop().stop()
    print("\n\nExit 0")
    os._exit(0)


async def run_schedule():
    while True:
        await asyncio.sleep(28800)
        await rq.parse_news()
        try:
            await rq.process_news()
        except Exception as e:
            print(e)



async def main():
    global signality
    await async_main()
    load_dotenv()

    token = os.getenv("TOKEN")
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(router)

    start_scheduler(bot)
    dp.update.middleware(HelloMiddleware())
    dp.update.middleware(CheckUserMiddleware())
    # asyncio.create_task(run_schedule())
    signality = asyncio.get_event_loop().run_in_executor(None, lambda : asyncio.run(run_schedule()))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit 0")