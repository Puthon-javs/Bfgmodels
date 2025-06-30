from aiogram import types, Dispatcher import random

Укажи свой ID здесь

OWNER_ID = 8174117949

war_users = {}

SHOP = { "военный завод": 4_000_000, "MG42": 500_000, "танк Т-90": 1_200_000, "вертолёт": 1_500_000, "бункер": 1_000_000 }

RANKS = [ (2_000_000, "👑 Генерал"), (500_000, "🛡 Командир"), (100_000, "🪖 Боец"), (0, "🔰 Новобранец") ]

async def warbase_handler(message: types.Message): uid = message.from_user.id text = message.text.lower().strip()

if uid not in war_users:
    war_users[uid] = {"balance": 10_000, "items": []}

p = war_users[uid]
reply = ""

if text == "военная база":
    reply = "🏰 Добро пожаловать в военную базу:\n"
    for item, price in SHOP.items():
        reply += f"🔹 {item} — {price} эктоплазмы\n"
    reply += "\nДля покупки: купить [название]"

elif text.startswith("купить"):
    item = text.replace("купить", "").strip()
    if item in SHOP:
        cost = SHOP[item]
        if p["balance"] >= cost:
            p["balance"] -= cost
            p["items"].append(item)
            reply = f"✅ Куплено: {item}. Остаток: {p['balance']}"
        else:
            reply = "❌ Недостаточно средств."
    else:
        reply = "❌ Нет такого объекта."

elif text == "мой арсенал":
    items = p["items"] or ["— пусто —"]
    reply = "🎒 Арсенал:\n" + "\n".join(f"• {i}" for i in items)
    reply += f"\n💰 Баланс: {p['balance']} эктоплазмы"

elif text == "мой ранг":
    bal = p["balance"]
    for required, rank in RANKS:
        if bal >= required:
            reply = f"🎖 Ваш ранг: {rank}\n💰 Эктоплазма: {bal}"
            break

elif text.startswith("бдать"):
    if uid != OWNER_ID:
        reply = "⛔ Только владелец может выдавать донат."
    elif not message.reply_to_message:
        reply = "📩 Используйте в ответ на сообщение игрока. Пример: бдать 10000"
    else:
        parts = text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            reply = "❌ Укажите сумму: бдать 10000"
        else:
            amount = int(parts[1])
            target_id = message.reply_to_message.from_user.id
            if war_users[uid]["balance"] < amount:
                reply = "❌ Недостаточно средств у отправителя."
            else:
                war_users[uid]["balance"] -= amount
                if target_id not in war_users:
                    war_users[target_id] = {"balance": 0, "items": []}
                war_users[target_id]["balance"] += amount
                reply = f"✅ Переведено {amount} эктоплазмы. Остаток: {war_users[uid]['balance']}"

else:
    reply = "❓ Неизвестная команда. Доступно: военная база, купить, мой арсенал, мой ранг, бдать (только для владельца)"

await message.answer(reply)

def register_handlers(dp: Dispatcher): dp.register_message_handler(warbase_handler, lambda m: m.text and m.chat.type in ["private", "supergroup"])

