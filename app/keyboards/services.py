from datetime import date, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

AVAILABLE_TIMES = ("10:00", "12:00", "14:00", "16:00", "18:00", "20:00")


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


def masters_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Алексей", callback_data="master:Алексей")],
            [InlineKeyboardButton(text="Михаил", callback_data="master:Михаил")],
            [InlineKeyboardButton(text="Любой мастер", callback_data="master:Любой мастер")],
        ]
    )


def dates_menu() -> InlineKeyboardMarkup:
    buttons = []
    for offset in range(1, 8):
        value = date.today() + timedelta(days=offset)
        buttons.append(
            [
                InlineKeyboardButton(
                    text=value.strftime("%d.%m, %a"),
                    callback_data=f"date:{value.isoformat()}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def times_menu(unavailable: set[str] | None = None) -> InlineKeyboardMarkup:
    unavailable = unavailable or set()
    times = [value for value in AVAILABLE_TIMES if value not in unavailable]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=value, callback_data=f"time:{value}")
                for value in times[index : index + 2]
            ]
            for index in range(0, len(times), 2)
        ]
    )
