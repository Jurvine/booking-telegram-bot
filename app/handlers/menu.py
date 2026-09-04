from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from app.config import load_admin_ids
from app.keyboards.main import main_menu
from app.keyboards.services import (
    AVAILABLE_TIMES,
    dates_menu,
    masters_menu,
    services_menu,
    times_menu,
)
from app.states.booking import Booking
from app.storage import (
    cancel_booking,
    create_booking,
    get_active_bookings,
    get_unavailable_times,
    is_slot_available,
)

router = Router()

SERVICES = {
    "haircut": "Мужская стрижка — 1 500 ₽",
    "beard": "Оформление бороды — 900 ₽",
    "combo": "Стрижка + борода — 2 100 ₽",
}


@router.message(F.text == "Записаться")
async def show_services(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Выберите услугу:", reply_markup=services_menu())


@router.callback_query(F.data.startswith("service:"))
async def select_service(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = callback.data.split(":", maxsplit=1)[1]
    service_name = SERVICES.get(service_id)
    if service_name is None:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await callback.answer()
    await state.update_data(service=service_name)
    if callback.message:
        await callback.message.answer("Выберите мастера:", reply_markup=masters_menu())


@router.callback_query(F.data.startswith("master:"))
async def select_master(callback: CallbackQuery, state: FSMContext) -> None:
    master = callback.data.split(":", maxsplit=1)[1]
    await state.update_data(master=master)
    await callback.answer()
    if callback.message:
        await callback.message.answer("Выберите дату:", reply_markup=dates_menu())


@router.callback_query(F.data.startswith("date:"))
async def select_date(callback: CallbackQuery, state: FSMContext) -> None:
    booking_date = callback.data.split(":", maxsplit=1)[1]
    await state.update_data(date=booking_date)
    await callback.answer()
    if callback.message:
        data = await state.get_data()
        unavailable = get_unavailable_times(data["master"], booking_date)
        if unavailable == set(AVAILABLE_TIMES):
            await callback.message.answer("На эту дату свободного времени нет.")
            return
        await callback.message.answer(
            "Выберите время:", reply_markup=times_menu(unavailable)
        )


@router.callback_query(F.data.startswith("time:"))
async def select_time(callback: CallbackQuery, state: FSMContext) -> None:
    booking_time = callback.data.split(":", maxsplit=1)[1]
    data = await state.get_data()
    if not is_slot_available(data["master"], data["date"], booking_time):
        await callback.answer("Это время уже занято", show_alert=True)
        return
    await state.update_data(time=booking_time)
    await state.set_state(Booking.waiting_phone)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Отправьте номер телефона кнопкой ниже или напишите его сообщением.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Отправить телефон", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )


@router.message(Booking.waiting_phone, F.contact)
async def receive_contact(message: Message, state: FSMContext) -> None:
    await finish_booking(message, state, message.contact.phone_number)


@router.message(Booking.waiting_phone, F.text)
async def receive_phone_text(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    digits = "".join(character for character in phone if character.isdigit())
    if len(digits) < 10:
        await message.answer("Похоже, номер неполный. Введите его ещё раз.")
        return
    await finish_booking(message, state, phone)


async def finish_booking(message: Message, state: FSMContext, phone: str) -> None:
    data = await state.get_data()
    result = create_booking(
        user_id=message.from_user.id,
        service=data["service"],
        master=data["master"],
        booking_date=data["date"],
        booking_time=data["time"],
        phone=phone,
        client_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    if result is None:
        unavailable = get_unavailable_times(data["master"], data["date"])
        await state.set_state(None)
        await message.answer(
            "Пока вы вводили телефон, это время заняли. Выберите другое:",
            reply_markup=times_menu(unavailable),
        )
        return

    _, assigned_master = result
    await message.answer(
        "Запись подтверждена! ✅\n\n"
        f"Услуга: {data['service']}\n"
        f"Мастер: {assigned_master}\n"
        f"Дата: {data['date']}\n"
        f"Время: {data['time']}\n"
        f"Телефон: {phone}",
        reply_markup=main_menu(),
    )
    username = f"@{message.from_user.username}" if message.from_user.username else "без username"
    notification = (
        "Новая запись! ✂️\n\n"
        f"Клиент: {message.from_user.full_name} ({username})\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Телефон: {phone}\n"
        f"Услуга: {data['service']}\n"
        f"Мастер: {assigned_master}\n"
        f"Дата: {data['date']}\n"
        f"Время: {data['time']}"
    )
    for admin_id in load_admin_ids():
        try:
            await message.bot.send_message(admin_id, notification)
        except TelegramAPIError:
            # Ошибка одного администратора не должна ломать запись клиента.
            pass
    await state.clear()


@router.message(F.text == "Мои записи")
async def show_bookings(message: Message) -> None:
    bookings = get_active_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас пока нет активных записей.")
        return

    await message.answer("Ваши активные записи:")
    for booking in bookings:
        await message.answer(
            f"Услуга: {booking['service']}\n"
            f"Мастер: {booking['master']}\n"
            f"Дата: {booking['booking_date']}\n"
            f"Время: {booking['booking_time']}\n"
            f"Телефон: {booking['phone']}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отменить запись",
                            callback_data=f"cancel:{booking['id']}",
                        )
                    ]
                ]
            ),
        )


@router.callback_query(F.data.startswith("cancel:"))
async def cancel_user_booking(callback: CallbackQuery) -> None:
    booking_id = int(callback.data.split(":", maxsplit=1)[1])
    cancelled = cancel_booking(booking_id, callback.from_user.id)
    if not cancelled:
        await callback.answer("Запись уже отменена или не найдена", show_alert=True)
        return

    await callback.answer("Запись отменена")
    if callback.message:
        await callback.message.edit_text("Запись отменена ❌")


@router.message(F.text == "Контакты")
async def show_contacts(message: Message) -> None:
    await message.answer(
        "Барбершоп «Demo Cut»\n"
        "Ежедневно: 10:00–21:00\n"
        "Телефон: +7 (900) 000-00-00"
    )
