import hashlib
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import load_bot_token
from app.handlers.admin import router as admin_router
from app.handlers.menu import router as menu_router
from app.handlers.start import router as start_router

WEBHOOK_PATH = "/telegram-webhook"


async def health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def create_app() -> web.Application:
    token = load_bot_token()
    external_url = os.getenv("RENDER_EXTERNAL_URL")
    if not external_url:
        raise RuntimeError("Не найдена переменная RENDER_EXTERNAL_URL.")

    webhook_secret = hashlib.sha256(token.encode()).hexdigest()
    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)
    dispatcher.include_router(admin_router)
    dispatcher.include_router(menu_router)

    async def set_webhook() -> None:
        await bot.set_webhook(
            f"{external_url}{WEBHOOK_PATH}",
            secret_token=webhook_secret,
        )

    dispatcher.startup.register(set_webhook)

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=webhook_secret,
    ).register(app, path=WEBHOOK_PATH)
    setup_application(app, dispatcher, bot=bot)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
    )
