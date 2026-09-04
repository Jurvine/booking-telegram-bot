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


def load_admin_ids() -> set[int]:
    load_dotenv()
    raw_ids = os.getenv("ADMIN_IDS", "")
    try:
        return {int(value.strip()) for value in raw_ids.split(",") if value.strip()}
    except ValueError as error:
        raise RuntimeError(
            "ADMIN_IDS должен содержать Telegram ID через запятую."
        ) from error
