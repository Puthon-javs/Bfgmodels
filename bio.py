from aiogram import types, Dispatcher from user import BFGuser from assets.antispam import antispam, new_earning import random

active_players = set() players = {} squads = {}

@antispam async def biowar_handler(message: types.Message, user: BFGuser): uid = user.user_id text = message.text.lower().strip()

if text == "/bio_on":
    active_players.add(uid)
    await message.answer("🧬 Модуль Биовойна активирован. Введите команду или /помощь")
    return

if text == "/bio_off":
    active_players.discard(uid)
    await message.answer("🚪 Вы покинули модуль Биовойна.")
    return

if text == "/помощь":
    await message.answer(
        "📜 Команды Биовойны:\n"
        "вскрыть, поиск, синтез, использовать [предмет]\n"
        "магазин, торговец, транспорт, союз, рейд, PvP: вызов @ник / принять / удар / защита"
    )
    return

if uid not in active_players:
    return

if uid not in players:
    players[uid] = {
        "hp": 100, "infection": 0, "energy": 5, "components": 0,
        "inventory": ["аптечка", "противоядие"],
        "resources": 5, "base": 0, "vehicle": None, "squad": None
    }

p = players[uid]
reply = ""

if text == "вскрыть":
    p["components"] += 1
    reply = "🧪 Вы вскрыли зону и нашли компонент."

elif text == "поиск":
    found = random.choice(["🔩 металл", "🧬 биоматериал", "⚗️ реагенты"])
    p["inventory"].append(found)
    reply = f"🔍 Найден ресурс: {found}"

elif text.startswith("использовать"):
    item = text.replace("использовать", "").strip()
    if item in p["inventory"]:
        p["inventory"].remove(item)
        reply = f"✅ Использовано: {item}"
    else:
        reply = f"❌ У вас нет предмета: {item}"

elif text == "синтез":
    if p["components"] >= 3:
        p["inventory"].append("вакцина")
        p["components"] -= 3
        reply = "💉 Вы синтезировали вакцину."
    else:
        reply = "❌ Нужно минимум 3 компонента."

elif text.startswith("создать союз"):
    name = text.replace("создать союз", "").strip()
    squads[name] = [uid]
    p["squad"] = name
    reply = f"🛡️ Союз '{name}' создан."

elif text.startswith("вступить союз"):
    name = text.replace("вступить союз", "").strip()
    if name in squads:
        squads[name].append(uid)
        p["squad"] = name
        reply = f"🤝 Вы вступили в союз '{name}'"
    else:
        reply = "❌ Союз не найден."

elif text == "союз":
    reply = f"🛡️ Ваш союз: {p['squad'] or 'отсутствует'}"

elif text == "рейд":
    if p["squad"]:
        loot = random.randint(3, 8)
        p["resources"] += loot
        reply = f"⚔️ Рейд успешен! Получено {loot} ресурсов."
    else:
        reply = "❌ Вы не состоите в союзе."

else:
    reply = "🤖 Неизвестная команда. Напишите /помощь"

await message.answer(reply)
await new_earning(message)

def register_handlers(dp: Dispatcher): dp.register_message_handler( biowar_handler, lambda m: m.text and m.chat.type in ["private", "supergroup"] )

MODULE_DESCRIPTION = { "name": "🧬 Биовойна", "description": "Модуль: PvP, союз, рейды, торговцы, заражение и синтез. Стиль Iris." }

