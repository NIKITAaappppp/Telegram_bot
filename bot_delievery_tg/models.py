class OrderItem:
    def __init__(self, dish, dish_price, fries=None, sauce=None, drink=None, add=None, remove=None):
        self.dish = dish
        self.price = dish_price  # базовая цена меню
        self.fries = fries
        self.sauce = sauce
        self.drink = drink
        self.add = add
        self.remove = remove

        # добавляем цену соуса
        if sauce and sauce != "Без соуса":
            self.price += 0.69

        # добавляем цену добавок
        ADDON_PRICES = {"Огурчики": 0, "Бекон": 0.69, "Сыр": 0.69}
        if add and add in ADDON_PRICES:
            self.price += ADDON_PRICES[add]

    def details(self):
        parts = [
            f"Блюдо: {self.dish}",
            f"Картошка: {self.fries or '—'}",
            f"Соус: {self.sauce or '—'}",
            f"Напиток: {self.drink or '—'}",
            f"Добавить: {self.add or '—'}",
            f"Убрать: {self.remove or '—'}",
            f"Цена: {self.price:.2f}$"
        ]
        return "\n".join(parts)
