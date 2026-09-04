import os

from dotenv import load_dotenv


def load_bot_token() -> str:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN. Создайте файл .env по образцу .env.example."
        )
    return token

