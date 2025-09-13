from aiogram.fsm.state import StatesGroup, State

class RegisterAccount(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    waiting_for_password_confirmation = State()

class OrderFood(StatesGroup):
    waiting_for_dish = State()
    waiting_for_fries = State()
    waiting_for_sauce = State()
    waiting_for_drink = State()
    waiting_for_add = State()
    waiting_for_remove = State()
    waiting_for_pizza_choice = State()
    waiting_for_size = State()
    waiting_for_drink_pizza = State()
    waiting_for_payement_choice = State()

