from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Главное меню ---
text_main_menu = ["👤 Аккаунт", "🍴 Рестораны", "🛒 Корзина"]
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_main_menu[i:i+2]] for i in range(0, len(text_main_menu), 2)],
    resize_keyboard=True
)

# --- Аккаунт (неавторизован) ---
text_account_unauth = ["Регистрация", "Вход", "⬅️ Назад в меню"]
account_unauth_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_account_unauth[i:i+2]] for i in range(0, len(text_account_unauth), 2)],
    resize_keyboard=True
)

# --- Аккаунт (авторизован) ---
text_account_logged_in = ["💰 Мой баланс", "📦 Мои заказы", "🎁 Мои бонусы", "⬅️ Назад в меню", "🚪 Выйти из аккаунта"]
account_logged_in_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_account_logged_in[i:i+2]] for i in range(0, len(text_account_logged_in), 2)],
    resize_keyboard=True
)

# --- Рестораны ---
text_restaurants_menu = ["Game Burger", "Pizza Hub", "⬅️ Назад"]
restaurants_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_restaurants_menu[i:i+2]] for i in range(0, len(text_restaurants_menu), 2)],
    resize_keyboard=True
)

# --- Меню Game Burger ---
text_game_burger_menu = ["Гейм чизбургер", "Дабл гейм чизбургер", "Наггетсы 6 шт", "Наггетсы 12 шт", "⬅️ Назад к ресторанам"]
game_burger_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_game_burger_menu[i:i+2]] for i in range(0, len(text_game_burger_menu), 2)],
    resize_keyboard=True
)

# --- Картошка ---
text_fries_menu = ["Обычная фри", "Дипсы", "⬅️ Назад к блюдам"]
fries_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_fries_menu[i:i+2]] for i in range(0, len(text_fries_menu), 2)],
    resize_keyboard=True
)

# --- Соусы ---
text_sauce_menu = ["Кари", "Сырный", "Кисло-сладкий", "Без соуса", "⬅️ Назад к картошке"]
sauce_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_sauce_menu[i:i+2]] for i in range(0, len(text_sauce_menu), 2)],
    resize_keyboard=True
)

# --- Напитки ---
text_drink_menu = ["Кола", "Фанта", "Спрайт", "Без напитка", "⬅️ Назад к соусу"]
drink_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_drink_menu[i:i+2]] for i in range(0, len(text_drink_menu), 2)],
    resize_keyboard=True
)

# --- Добавки ---
text_add_menu = ["Огурчики", "Бекон", "Сыр", "Ничего", "⬅️ Назад к напитку"]
add_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_add_menu[i:i+2]] for i in range(0, len(text_add_menu), 2)],
    resize_keyboard=True
)

# --- Что убрать ---
text_remove_menu = ["Соль", "Огурчики", "Лук", "Сыр", "Котлету", "Ничего", "⬅️ Назад к добавкам"]
remove_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_remove_menu[i:i+2]] for i in range(0, len(text_remove_menu), 2)],
    resize_keyboard=True
)

# --- Баланс ---
text_balance_menu = ["💳 Пополнить баланс", "⬅️ Назад к аккаунту"]
balance_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_balance_menu[i:i+2]] for i in range(0, len(text_balance_menu), 2)],
    resize_keyboard=True
)

# --- Методы оплаты ---
text_payment_methods = ["💳 Карта", "🌍 PayPal", "₿ Крипта", "⬅️ Назад к балансу"]
payment_methods_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_payment_methods[i:i+2]] for i in range(0, len(text_payment_methods), 2)],
    resize_keyboard=True
)

# --- Корзина ---
text_cart_menu = ["🗑️ Очистить корзину", "🧾 Оформить заказ", "⬅️ Назад в меню"]
cart_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_cart_menu[i:i+2]] for i in range(0, len(text_cart_menu), 2)],
    resize_keyboard=True
)

# --- Бонусы ---
text_bonuses_menu = ["⬅️ Назад к аккаунту"]
bonuses_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_bonuses_menu[i:i+2]] for i in range(0, len(text_bonuses_menu), 2)],
    resize_keyboard=True
)

# --- Pizza Hub main menu ---
text_pizza_hub_menu = ["🍕 Пицца", "⬅️ Назад к ресторанам"]
pizza_hub_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_pizza_hub_menu[i:i+2]] for i in range(0, len(text_pizza_hub_menu), 2)],
    resize_keyboard=True
)

# --- Выбор пиццы ---
text_pizza_choices = ["Пепперони", "4 сыра", "Боварская", "Мясная", "⬅️ Назад к Pizza Hub"]
pizza_choices_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_pizza_choices[i:i+2]] for i in range(0, len(text_pizza_choices), 2)],
    resize_keyboard=True
)

# --- Выбор размера пиццы ---
text_pizza_size = ["30 см", "60 см", "⬅️ Назад к выбору пиццы"]
pizza_size_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_pizza_size[i:i+2]] for i in range(0, len(text_pizza_size), 2)],
    resize_keyboard=True
)

# --- Напитки для Pizza Hub ---
text_drink_menu_pizza = ["Кола", "Фанта", "Спрайт", "Без напитка", "⬅️ Назад к Pizza Hub"]
drink_menu_pizza_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_drink_menu_pizza[i:i+2]] for i in range(0, len(text_drink_menu_pizza), 2)],
    resize_keyboard=True
)
# --- Выбор оплаты при оформлении заказа ---
text_payment_choice = ["💰 Оплатить балансом", "🎁 Оплатить бонусами", "⬅️ Назад к корзине"]
payment_choice_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=t) for t in text_payment_choice[i:i+2]] for i in range(0, len(text_payment_choice), 2)],
    resize_keyboard=True
)