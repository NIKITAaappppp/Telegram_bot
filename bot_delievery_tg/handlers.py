import json
from pathlib import Path
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import *
from states import RegisterAccount, OrderFood
from models import OrderItem

router = Router()

USERS_FILE = Path("users.json")
SESSIONS_FILE = Path("sessions.json")

# --- глобальные данные ---
users_db = {}
current_sessions = {}
login_attempts = {}
user_cart = {}

# --- helpers ---
def load_json(file_path: Path, default=None, key_int: bool = False):
    """Загрузка JSON с файла, ключи приводятся к int если key_int=True"""
    default = default or {}
    if not file_path.exists():
        return default
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if key_int:
            return {int(k): v for k, v in data.items()}
        return data
    except Exception:
        return default

def save_json(file_path: Path, data: dict, key_str: bool = False):
    """Сохраняем JSON в файл, ключи приводятся к str если key_str=True"""
    try:
        if key_str:
            data = {str(k): v for k, v in data.items()}
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Ошибка при сохранении {file_path}: {e}")

def is_valid_username(u: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,16}", u))  # добавлен лимит длины

def password_ok(p: str) -> bool:
    """Минимум 8 символов, хотя бы одна заглавная буква и спецсимвол"""
    return len(p) >= 8 and bool(re.search(r"[A-Z]", p)) and bool(re.search(r"[!@#$%^&*]", p))

async def proceed_to_password(state: FSMContext, action: str, username: str):
    await state.update_data(username=username)
    await state.set_state(RegisterAccount.waiting_for_password)
    msg = "Введите пароль"
    if action == "register":
        msg += " (мин 8 символов, 1 заглавная буква, 1 спецсимвол !@#$%^&*)"
    await state.get_data()
    await state.update_data(username=username)
    return msg

def require_login(chat_id: int):
    """Возвращает username, если пользователь авторизован, иначе None"""
    return current_sessions.get(chat_id)

# --- инициализация данных ---
users_db = load_json(USERS_FILE, default={})
current_sessions = load_json(SESSIONS_FILE, default={}, key_int=True)

# --- START ---
@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    chat = message.chat.id
    if chat in current_sessions:
        user = current_sessions[chat]
        await message.answer(f"С возвращением, {user}!", reply_markup=account_logged_in_kb)
    else:
        await message.answer("Здравствуйте! 👋\nВас приветствует Game Delivery.", reply_markup=main_menu_kb)


# --- ACCOUNT MENU ---
@router.message(F.text == "👤 Аккаунт")
async def account_menu(message: Message, state: FSMContext):
    await state.clear()
    user = current_sessions.get(message.chat.id)
    if user:
        await message.answer(f"Вы вошли как {user}", reply_markup=account_logged_in_kb)
    else:
        await message.answer("Раздел аккаунта:", reply_markup=account_unauth_kb)


# --- BACK BUTTONS ---
BACK_MAP = {
    "⬅️ Назад": ("Главное меню:", main_menu_kb),
    "⬅️ Назад в меню": ("Главное меню:", main_menu_kb),
    "⬅️ Назад к аккаунту": ("Раздел аккаунта:", account_logged_in_kb),
    "⬅️ Назад к ресторанам": ("Выберите ресторан:", restaurants_menu_kb),
    "⬅️ Назад к блюдам": ("Выберите блюдо:", game_burger_menu_kb),
    "⬅️ Назад к картошке": ("Выберите картошку:", fries_menu_kb),
    "⬅️ Назад к соусу": ("Выберите соус:", sauce_menu_kb),
    "⬅️ Назад к напитку": ("Выберите напиток:", drink_menu_kb),
    "⬅️ Назад к добавкам": ("Выберите добавку:", add_menu_kb),
    "⬅️ Назад к балансу": ("Ваш баланс:", balance_menu_kb),
    "⬅️ Назад к корзине": ("Ваша корзина:", cart_menu_kb),
    "⬅️ Назад к Pizza Hub": ("Меню Pizza Hub:", pizza_hub_menu_kb),
    "⬅️ Назад к выбору пиццы": ("Выберите пиццу:", pizza_choices_kb),
}

@router.message(F.text.in_(BACK_MAP.keys()))
async def universal_back(message: Message, state: FSMContext):
    await state.clear()
    text, kb = BACK_MAP[message.text]
    await message.answer(text, reply_markup=kb)


# --- REGISTRATION & LOGIN ---
@router.message(F.text.in_(["Регистрация", "Вход"]))
async def start_auth(message: Message, state: FSMContext):
    await state.clear()
    action = "register" if message.text == "Регистрация" else "login"

    user = current_sessions.get(message.chat.id)
    if user:
        await message.answer(f"Вы уже вошли как {user}. Для новой регистрации выйдите из аккаунта.")
        return

    await state.update_data(action=action)
    await state.set_state(RegisterAccount.waiting_for_username)
    await message.answer("Введите никнейм:")

# --- HANDLE USERNAME ---
@router.message(RegisterAccount.waiting_for_username)
async def handle_username(message: Message, state: FSMContext):
    data = await state.get_data()
    action = data.get("action")
    username = message.text.strip()

    if not is_valid_username(username):
        await message.answer("Неверный никнейм. Допустимы латиница, цифры и _")
        return

    if action == "register":
        if username in users_db:
            await message.answer("Такой никнейм уже существует.")
            return
    elif action == "login":
        if username not in users_db:
            await message.answer("Такого пользователя нет.")
            return
        login_attempts.setdefault(username, 3)

    msg = await proceed_to_password(state, action, username)
    await message.answer(msg)


# --- HANDLE PASSWORD & REGISTRATION CONFIRMATION ---
@router.message(RegisterAccount.waiting_for_password)
async def handle_password(message: Message, state: FSMContext):
    data = await state.get_data()
    action = data.get("action")
    username = data.get("username")
    password = message.text.strip()

    if action == "register":
        if not password_ok(password):
            await message.answer(
                "Пароль не подходит. Требования: минимум 8 символов, заглавная буква и спецсимвол (!@#$%^&*)"
            )
            return
        await state.update_data(password=password)
        await state.set_state(RegisterAccount.waiting_for_password_confirmation)
        await message.answer("Подтвердите пароль:")

    elif action == "login":
        if username not in users_db or "password" not in users_db[username]:
            await message.answer("Пользователь не найден. Начните вход заново.")
            await state.clear()
            return

        if password != users_db[username]["password"]:
            login_attempts[username] = login_attempts.get(username, 3) - 1
            if login_attempts[username] <= 0:
                await message.answer("Вы исчерпали попытки. Попробуйте позже.")
                await state.clear()
                return
            await message.answer(f"Неверный пароль. Осталось попыток: {login_attempts[username]}")
            return

        # успешный вход
        current_sessions[message.chat.id] = username
        save_json(SESSIONS_FILE, current_sessions, key_str=True)
        await state.clear()
        await message.answer(f"✅ Вы вошли как {username}.", reply_markup=account_logged_in_kb)


@router.message(RegisterAccount.waiting_for_password_confirmation)
async def handle_password_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    password = data.get("password")
    confirm = message.text.strip()
    username = data.get("username")

    if password != confirm:
        await message.answer("Пароли не совпадают. Введите пароль снова.")
        await state.set_state(RegisterAccount.waiting_for_password)
        return

    # создаём нового пользователя
    users_db[username] = {
        "password": password,
        "balance": 0.0,
        "bonuses": 0,
        "orders": []
    }
    save_json(USERS_FILE, users_db)

    # сразу авторизуем
    current_sessions[message.chat.id] = username
    save_json(SESSIONS_FILE, current_sessions, key_str=True)

    await state.clear()
    await message.answer(
        f"✅ Вы успешно зарегистрированы и вошли как {username}.",
        reply_markup=account_logged_in_kb
    )



# --- LOGOUT ---
@router.message(F.text == "🚪 Выйти из аккаунта")
async def logout_handler(message: Message):
    chat = message.chat.id
    current_sessions.pop(chat, None)
    save_json(Path(SESSIONS_FILE), current_sessions, key_str=True)
    await message.answer("Вы вышли из аккаунта.", reply_markup=main_menu_kb)


# --- BALANCE ---
@router.message(F.text == "💰 Мой баланс")
async def my_balance(message: Message):
    chat = message.chat.id
    user = require_login(chat)
    if not user:
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return
    bal = users_db[user]["balance"]
    await message.answer(f"Ваш баланс: {bal:.2f}$", reply_markup=balance_menu_kb)


@router.message(F.text == "💳 Пополнить баланс")
async def top_up_start(message: Message):
    chat = message.chat.id
    user = require_login(chat)
    if not user:
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return
    await message.answer("Выберите способ оплаты:", reply_markup=payment_methods_kb)


@router.message(F.text.in_(["💳 Карта", "🌍 PayPal", "₿ Крипта"]))
async def top_up_process(message: Message):
    chat = message.chat.id
    user = require_login(chat)
    if not user:
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return

    AMOUNT = 10.0  # фиксированная сумма пополнения

    # Обновляем баланс
    users_db[user]["balance"] += AMOUNT
    save_json(Path(USERS_FILE), users_db)  # используем новую функцию сохранения JSON

    # Ответ пользователю
    await message.answer(
        f"Баланс пополнен на {AMOUNT:.2f}$. Текущий баланс: {users_db[user]['balance']:.2f}$",
        reply_markup=account_logged_in_kb
    )

# --- RESTAURANTS ---
@router.message(F.text == "🍴 Рестораны")
async def restaurants_list(message: Message, state: FSMContext):
    user = require_login(message.chat.id)
    if not user:
        await message.answer("Для просмотра ресторанов нужно войти в аккаунт.", reply_markup=account_unauth_kb)
        return

    await state.clear()
    await message.answer("Выберите ресторан:", reply_markup=restaurants_menu_kb)


@router.message(F.text == "Game Burger")
async def game_burger_menu(message: Message, state: FSMContext):
    if not require_login(message.chat.id):
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return

    await state.clear()
    await message.answer("Меню Game Burger:", reply_markup=game_burger_menu_kb)
    await state.set_state(OrderFood.waiting_for_dish)

@router.message(F.text == "Pizza Hub")
async def pizza_hub_menu(message: Message, state: FSMContext):
    if not require_login(message.chat.id):
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return
    await state.clear()
    await message.answer("Меню Pizza Hub:", reply_markup=pizza_hub_menu_kb)
    await state.set_state(OrderFood.waiting_for_pizza_choice)  





# --- PRICES ---
DISH_PRICES = {"Гейм чизбургер":6.99,"Дабл гейм чизбургер":10.99,"Наггетсы 6 шт":6.99,"Наггетсы 12 шт":10.99}
FRIES_PRICES = {"Обычная фри":2.99,"Дипсы":1.49}
SAUCE_PRICES = {"Кари":0.69,"Сырный":0.69,"Кисло-сладкий":0.69,"Без соуса":0.0}
DRINK_PRICES = {"Кола":1.99,"Фанта":1.99,"Спрайт":1.99,"Без напитка":0.0}
ADD_PRICES = {"Огурчики":0.0,"Бекон":0.69,"Сыр":0.69,"Ничего":0.0}
REMOVE_PRICES = {"Соль": 0.0, "Огурчики": 0.0, "Лук": 0.0, "Сыр": 0.0, "Котлету": 0.0, "Ничего": 0.0}


def calculate_item_price(item: OrderItem) -> float:
    return (
        DISH_PRICES.get(item.dish, 0) +
        FRIES_PRICES.get(item.fries, 0) +
        SAUCE_PRICES.get(item.sauce.split(" -")[0] if item.sauce else "Без соуса", 0) +
        DRINK_PRICES.get(item.drink, 0) +
        ADD_PRICES.get(item.add.split(" -")[0] if item.add else "Ничего", 0)
    )


# --- PIZZA HUB ---
PIZZA_PRICES = {"Пепперони":10.99,"4 сыра":11.99,"Боварская":12.99,"Мясная":13.99}
PIZZA_SIZE_MULTIPLIER = {"30 см":1, "60 см":1.8}
DRINK_PRICES_PIZZA = {"Кола":1.99,"Фанта":1.99,"Спрайт":1.99,"Без напитка":0.0}

def calculate_pizza_total(pizza_name: str, size: str, drink: str) -> float:
    base = PIZZA_PRICES.get(pizza_name, 0)
    multiplier = PIZZA_SIZE_MULTIPLIER.get(size, 1)
    drink_price = DRINK_PRICES_PIZZA.get(drink, 0)
    return round(base * multiplier + drink_price, 2)

# --- ORDER FLOW ---
@router.message(OrderFood.waiting_for_dish)
async def order_choose_dish(message: Message, state: FSMContext):
    dish = message.text.strip()
    if dish not in DISH_PRICES:
        await message.answer("Выберите блюдо из меню.")
        return
    await state.update_data(dish=dish)
    await message.answer("Выберите картошку:", reply_markup=fries_menu_kb)
    await state.set_state(OrderFood.waiting_for_fries)

@router.message(OrderFood.waiting_for_fries)
async def order_choose_fries(message: Message, state: FSMContext):
    choice = message.text.strip()
    if choice not in FRIES_PRICES:
        await message.answer("Выберите картошку из списка.")
        return
    await state.update_data(fries=choice)
    await message.answer("Выберите соус:", reply_markup=sauce_menu_kb)
    await state.set_state(OrderFood.waiting_for_sauce)

@router.message(OrderFood.waiting_for_sauce)
async def order_choose_sauce(message: Message, state: FSMContext):
    choice = message.text.strip().split(" -")[0]
    if choice not in SAUCE_PRICES:
        await message.answer("Выберите соус из списка.")
        return
    await state.update_data(sauce=choice)
    await message.answer("Выберите напиток:", reply_markup=drink_menu_kb)
    await state.set_state(OrderFood.waiting_for_drink)

@router.message(OrderFood.waiting_for_drink)
async def order_choose_drink(message: Message, state: FSMContext):
    choice = message.text.strip().split(" -")[0]
    if choice not in DRINK_PRICES:
        await message.answer("Выберите напиток из списка.")
        return
    await state.update_data(drink=choice)
    await message.answer("Выберите добавку:", reply_markup=add_menu_kb)
    await state.set_state(OrderFood.waiting_for_add)

@router.message(OrderFood.waiting_for_add)
async def order_choose_add(message: Message, state: FSMContext):
    choice = message.text.strip().split(" -")[0]
    if choice not in ADD_PRICES:
        await message.answer("Выберите добавку из списка.")
        return
    await state.update_data(add=choice)
    await message.answer("Что убрать? (опционально)", reply_markup=remove_menu_kb)
    await state.set_state(OrderFood.waiting_for_remove)

@router.message(OrderFood.waiting_for_remove)
async def order_choose_remove(message: Message, state: FSMContext):
    user_input = message.text.strip().split(" -")[0]  # берём текст кнопки

    if user_input not in REMOVE_PRICES:
        await message.answer("Выберите ингредиент из списка.", reply_markup=remove_menu_kb)
        return

    await state.update_data(remove=user_input)
    data = await state.get_data()

    # создаём объект заказа
    item = OrderItem(
        dish=data["dish"],
        dish_price=DISH_PRICES.get(data["dish"], 0),  # базовая цена блюда
        fries=data.get("fries"),
        sauce=data.get("sauce"),
        drink=data.get("drink"),
        add=data.get("add"),
        remove=data.get("remove")
    )

    # пересчёт цены
    item.price = calculate_item_price(item)

    # добавляем в корзину
    chat = message.chat.id
    user_cart.setdefault(chat, []).append(item)

    await state.clear()
    await message.answer(f"✅ Добавлено в корзину:\n{item.details()}", reply_markup=main_menu_kb)





# --- Переход в Pizza Hub ---
@router.message(OrderFood.waiting_for_pizza_choice)
async def pizza_choices_handler(message: Message, state: FSMContext):
    if message.text == "🍕 Пицца":
        await message.answer("Выберите пиццу:", reply_markup=pizza_choices_kb)
        return
    pizza = message.text.strip()
    if pizza not in PIZZA_PRICES:
        await message.answer("Выберите пиццу из списка.")
        return
    await state.update_data(pizza=pizza)
    await message.answer("Выберите размер пиццы:", reply_markup=pizza_size_kb)
    await state.set_state(OrderFood.waiting_for_size)

@router.message(OrderFood.waiting_for_size)
async def choose_pizza_size(message: Message, state: FSMContext):
    size = message.text.strip()
    if size not in PIZZA_SIZE_MULTIPLIER:  # "⬅️ Назад к выбору пиццы" — universal_back
        await message.answer("Выберите размер пиццы из списка.")
        return
    await state.update_data(size=size)
    await message.answer("Выберите напиток:", reply_markup=drink_menu_pizza_kb)
    await state.set_state(OrderFood.waiting_for_drink_pizza)

@router.message(OrderFood.waiting_for_drink_pizza)
async def choose_pizza_drink(message: Message, state: FSMContext):
    drink = message.text.strip()
    if drink not in DRINK_PRICES_PIZZA:  # "⬅️ Назад к Pizza Hub" или "⬅️ Назад к выбору пиццы" — universal_back
        await message.answer("Выберите напиток из списка.")
        return

    await state.update_data(drink=drink)
    data = await state.get_data()
    total_price = calculate_pizza_total(data["pizza"], data["size"], data["drink"])

    item = OrderItem(
        dish=data["pizza"],
        dish_price=total_price,
        fries=None,
        sauce=None,
        drink=data["drink"],
        add=None,
        remove=None
    )

    chat = message.chat.id
    user_cart.setdefault(chat, []).append(item)
    await state.clear()
    await message.answer(f"✅ Добавлено в корзину:\n{item.details()}", reply_markup=main_menu_kb)


# --- UNIVERSAL ACCOUNT ACTIONS (с отладкой) ---
@router.message(F.text.in_(["📦 Мои заказы", "💰 Мой баланс", "🎁 Мои бонусы", "🚪 Выйти из аккаунта"]))
async def universal_account_actions(message: Message, state: FSMContext):
    chat = message.chat.id
    state_data = await state.get_state()
    print(f"[DEBUG] chat {chat} pressed '{message.text}', current state: {state_data}")
    
    await state.clear()  # сбрасываем FSM

    user = current_sessions.get(chat)
    if not user:
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return

    text = message.text

    if text == "📦 Мои заказы":
        orders = users_db[user].get("orders", [])
        if not orders:
            await message.answer("У вас нет заказов.", reply_markup=account_logged_in_kb)
            return
        msg = ""
        for idx, order in enumerate(orders, 1):
            items_text = "\n".join(order["items"])
            msg += f"Заказ #{idx}:\n{items_text}\nСумма: {order['total']:.2f}$\nОплата: {order['payment']}\n\n"
        await message.answer(msg, reply_markup=account_logged_in_kb)

    elif text == "💰 Мой баланс":
        bal = users_db[user]["balance"]
        await message.answer(f"Ваш баланс: {bal:.2f}$", reply_markup=balance_menu_kb)

    elif text == "🎁 Мои бонусы":
        bonuses = users_db[user].get("bonuses", 0)
        await message.answer(f"🎁 У вас {bonuses} бонусов.", reply_markup=bonuses_menu_kb)

    elif text == "🚪 Выйти из аккаунта":
        current_sessions.pop(chat, None)
        save_json(Path(SESSIONS_FILE), current_sessions, key_str=True)
        await message.answer("Вы вышли из аккаунта.", reply_markup=main_menu_kb)

    



# --- CART ---
@router.message(F.text == "🛒 Корзина")
async def view_cart(message: Message):
    chat = message.chat.id
    items = user_cart.get(chat, [])
    if not items:
        await message.answer("Корзина пуста.", reply_markup=main_menu_kb)
        return
    text = "\n\n".join([f"{i.dish} - {i.price:.2f}$" for i in items])
    await message.answer(f"Ваша корзина:\n{text}", reply_markup=cart_menu_kb)

@router.message(F.text == "🗑️ Очистить корзину")
async def clear_cart(message: Message):
    chat = message.chat.id
    user_cart[chat] = []
    await message.answer("Корзина очищена.", reply_markup=main_menu_kb)





# --- ОФОРМЛЕНИЕ ЗАКАЗА ---
@router.message(F.text == "🧾 Оформить заказ")
async def checkout_start(message: Message, state: FSMContext):
    chat = message.chat.id
    user = current_sessions.get(chat)
    if not user:
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        return

    items = user_cart.get(chat, [])
    if not items:
        await message.answer("Корзина пуста.", reply_markup=main_menu_kb)
        return

    total = sum(item.price for item in items)
    await state.update_data(checkout_total=total, checkout_chat=chat)

    # Показываем сумму и выбор оплаты
    await message.answer(
        f"Сумма заказа: {total:.2f}$\nВыберите способ оплаты:",
        reply_markup=payment_choice_kb
    )
    await state.set_state(OrderFood.waiting_for_payement_choice)


# --- ВЫБОР ОПЛАТЫ ---
@router.message(OrderFood.waiting_for_payement_choice)
async def process_checkout_payment(message: Message, state: FSMContext):
    chat = message.chat.id
    user = current_sessions.get(chat)
    if not user:
        await message.answer("Войдите в аккаунт.", reply_markup=account_unauth_kb)
        await state.clear()
        return

    # Кнопка "назад к корзине"
    if message.text == "⬅️ Назад к корзине":
        await state.clear()
        items = user_cart.get(chat, [])
        if not items:
            await message.answer("Корзина пуста.", reply_markup=main_menu_kb)
        else:
            text = "\n\n".join([f"{i.dish} - {i.price:.2f}$" for i in items])
            await message.answer(f"Ваша корзина:\n{text}", reply_markup=cart_menu_kb)
        return

    items = user_cart.get(chat, [])
    if not items:
        await message.answer("Корзина пуста.", reply_markup=main_menu_kb)
        await state.clear()
        return

    total = sum(i.price for i in items)

    if message.text == "💰 Оплатить балансом":
        if users_db[user]["balance"] < total:
            await message.answer("❌ Недостаточно средств на балансе.", reply_markup=balance_menu_kb)
            return
        users_db[user]["balance"] -= total
        users_db[user]["bonuses"] += 100
        payment_str = f"{total:.2f} $"
    elif message.text == "🎁 Оплатить бонусами":
        if users_db[user]["bonuses"] < 500:
            await message.answer("❌ Недостаточно бонусов (нужно 500).", reply_markup=bonuses_menu_kb)
            return
        users_db[user]["bonuses"] -= 500
        payment_str = "500 бонусов"
    else:
        await message.answer("Выберите корректный способ оплаты.")
        return

    # Добавляем заказ в базу
    order_summary = [i.details() for i in items]
    users_db[user].setdefault("orders", []).append({
        "items": order_summary,
        "total": total,
        "payment": payment_str
    })

    # Очищаем корзину и сохраняем
    user_cart[chat] = []
    save_json(Path(USERS_FILE), users_db) 

    await message.answer(
        f"✅ Заказ оформлен!\nСписано: {payment_str}.\n"
        f"{'Начислено 100 бонусов.' if message.text == '💰 Оплатить балансом' else ''}\n\n"
        f"💵 Баланс: {users_db[user]['balance']:.2f}$\n"
        f"🎁 Бонусы: {users_db[user]['bonuses']}",
        reply_markup=main_menu_kb
    )
    await state.clear

