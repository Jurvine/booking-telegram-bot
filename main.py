import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_bot_token
from app.handlers.menu import router as menu_router
from app.handlers.start import router as start_router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=load_bot_token())
    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)
    dispatcher.include_router(menu_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
