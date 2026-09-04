from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.keyboards.services import services_menu

router = Router()

SERVICES = {
    "haircut": "Мужская стрижка — 1 500 ₽",
    "beard": "Оформление бороды — 900 ₽",
    "combo": "Стрижка + борода — 2 100 ₽",
}


@router.message(F.text == "Записаться")
async def show_services(message: Message) -> None:
    await message.answer("Выберите услугу:", reply_markup=services_menu())


@router.callback_query(F.data.startswith("service:"))
async def select_service(callback: CallbackQuery) -> None:
    service_id = callback.data.split(":", maxsplit=1)[1]
    service_name = SERVICES.get(service_id)
    if service_name is None:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await callback.answer()
    if callback.message:
        await callback.message.answer(
            f"Вы выбрали: {service_name}\n\nСледующий шаг — выбор мастера."
        )


@router.message(F.text == "Мои записи")
async def show_bookings(message: Message) -> None:
    await message.answer("У вас пока нет активных записей.")


@router.message(F.text == "Контакты")
async def show_contacts(message: Message) -> None:
    await message.answer(
        "Барбершоп «Demo Cut»\n"
        "Ежедневно: 10:00–21:00\n"
        "Телефон: +7 (900) 000-00-00"
    )

