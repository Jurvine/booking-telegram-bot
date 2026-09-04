from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def services_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Мужская стрижка — 1 500 ₽",
                    callback_data="service:haircut",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Оформление бороды — 900 ₽",
                    callback_data="service:beard",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Стрижка + борода — 2 100 ₽",
                    callback_data="service:combo",
                )
            ],
        ]
    )

