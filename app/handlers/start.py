from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.main import main_menu

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Здравствуйте! Я помогу записаться на услугу.\n\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=main_menu(),
    )

