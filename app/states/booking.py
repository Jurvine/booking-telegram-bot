from aiogram.fsm.state import State, StatesGroup


class Booking(StatesGroup):
    waiting_phone = State()

