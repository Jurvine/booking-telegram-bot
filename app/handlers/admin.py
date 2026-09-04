from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import load_admin_ids
from app.storage import cancel_booking_by_admin, get_all_active_bookings

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in load_admin_ids()


@router.message(Command("myid"))
async def show_user_id(message: Message) -> None:
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")


@router.message(Command("admin"))
async def show_admin_panel(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Нет доступа к панели администратора.")
        return

    bookings = get_all_active_bookings()
    if not bookings:
        await message.answer("Активных записей пока нет.")
        return

    await message.answer(f"Активных записей: {len(bookings)}")
    for booking in bookings:
        username = f"@{booking['username']}" if booking["username"] else "без username"
        client = booking["client_name"] or "Клиент"
        await message.answer(
            f"Запись №{booking['id']}\n"
            f"Клиент: {client} ({username})\n"
            f"Telegram ID: {booking['user_id']}\n"
            f"Телефон: {booking['phone']}\n"
            f"Услуга: {booking['service']}\n"
            f"Мастер: {booking['master']}\n"
            f"Дата: {booking['booking_date']}\n"
            f"Время: {booking['booking_time']}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отменить запись",
                            callback_data=f"admin_cancel:{booking['id']}",
                        )
                    ]
                ]
            ),
        )


@router.callback_query(F.data.startswith("admin_cancel:"))
async def admin_cancel_booking(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    booking_id = int(callback.data.split(":", maxsplit=1)[1])
    if not cancel_booking_by_admin(booking_id):
        await callback.answer("Запись уже отменена", show_alert=True)
        return

    await callback.answer("Запись отменена")
    if callback.message:
        await callback.message.edit_text(
            f"Запись №{booking_id} отменена администратором ❌"
        )
