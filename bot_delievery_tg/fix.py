import json
import re

USERS_FILE = "users.json"

with open(USERS_FILE, "r", encoding="utf-8") as f:
    users_db = json.load(f)

for user, data in users_db.items():
    orders = data.get("orders", [])
    new_orders = []
    for order in orders:
        if isinstance(order, dict) and "items" in order:
            new_orders.append(order)
        elif isinstance(order, str):
            # Попытка извлечь сумму из текста (например "Название - 12.99$")
            m = re.search(r"([\d.]+)\$", order)
            total = float(m.group(1)) if m else 0.0
            # Извлекаем название блюда без суммы
            name = re.sub(r" - [\d.]+\$", "", order) if m else order
            new_orders.append({
                "items": [name],
                "total": total,
                "payment": "Неизвестно"
            })
        else:
            continue
    users_db[user]["orders"] = new_orders

with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump(users_db, f, ensure_ascii=False, indent=4)

print("✅ users.json обновлён!")
