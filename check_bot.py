import asyncio

from aiogram import Bot

from app.config import load_bot_token


async def main() -> None:
    async with Bot(token=load_bot_token()) as bot:
        bot_info = await bot.get_me()
        print(f"Подключение успешно: {bot_info.full_name} (@{bot_info.username})")


if __name__ == "__main__":
    asyncio.run(main())

