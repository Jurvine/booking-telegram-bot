from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Записаться")],
            [KeyboardButton(text="Мои записи"), KeyboardButton(text="Контакты")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )

