from aiogram import types, Dispatcher from user import BFGuser from assets.antispam import antispam, new_earning import random

active_players = set() players = {} mutant_locations = {} pvp_duels = {} soups = {}  # союзы resources = ["🔩 металл", "🧬 биоматериал", "⚗️ реагенты"] weapons = [ {"название": "🔫 пистолет", "тип": "пистолет", "урон": 15}, {"название": "🔪 нож", "тип": "холодное", "урон": 10}, {"название": "⚡ электрошокер", "тип": "электро", "урон": 20}, {"название": "AK-47", "тип": "автомат", "урон": 30}, {"название": "MG3", "тип": "пулемёт", "урон": 50}, {"название": "🚁 Вертолёт", "тип": "техника", "урон": 100} ]

shop_items = { "аптечка": {"cost": 2}, "противоядие": {"cost": 3}, "AK-47": {"cost": 5}, "MG3": {"cost": 10}, "джип": {"cost": 8}, "вертолёт": {"cost": 15} }

trader_goods = ["противоядие", "MG3", "мотоцикл"]

locations = { "🧪 Лаборатория": {"danger": 2}, "🏚️ Госпиталь": {"danger": 4}, "🌆 Город-призрак": {"danger": 5}, "🚧 Карантинная зона": {"danger": 6}, "🔥 Зона-X": {"danger": 9, "босс": "💀 Мозг-Король"}, "🧬 Котёл": {"danger": 8, "босс": "👹 Генетический титан"} }

mutants = [ {"name": "Мутант-Х", "power": 3}, {"name": "Тварь зоны", "power": 4}, {"name": "Ревущий", "power": 2}, {"name": "Бессмертный", "power": 5} ]

@antispam async def biowar_handler(message: types.Message, user: BFGuser): uid = user.user_id text = message.text.lower().strip() uname = user.username or str(uid)

if text == "/bio_on":
    active_players.add(uid)
    await message.answer("🧬 Модуль Биовойна активирован. Введите команду или /помощь")
    return
if text == "/bio_off":
    active_players.discard(uid)
    await message.answer("🚪 Вы покинули модуль Биовойна.")
    return
if text == "/помощь":
    await message.answer("📜 Команды: вскрыть, поиск, синтез, использовать, магазин, транспорт, торговец, база, союз, рейд, PvP (вызов, принять, удар)")
    return
if uid not in active_players:
    return

if uid not in players:
    players[uid] = {
        "hp": 100, "infection": 0, "energy": 5, "components": 0,
        "location": random.choice(list(locations)),
        "inventory": ["аптечка", "противоядие"],
        "resources": 5, "base": 0, "vehicle": None, "squad": None
    }

p = players[uid]
reply = ""

if text == "торговец":
    reply = "🧑‍🌾 Торговец предлагает:\n" + "\n".join(f"{item} — 4 ресурса" for item in trader_goods)
elif text.startswith("купить у торговца"):
    item = text.replace("купить у торговца", "").strip()
    if item in trader_goods and p["resources"] >= 4:
        p["inventory"].append(item)
        p["resources"] -= 4
        reply = f"✅ Куплено у торговца: {item}"
    else:
        reply = "❌ Нет такого предмета или недостаточно ресурсов."
elif text == "транспорт":
    reply = f"🚙 Ваш транспорт: {p['vehicle'] or 'нет'}"
elif text.startswith("починить транспорт"):
    if p["vehicle"]:
        p["resources"] -= 2
        reply = f"🔧 Транспорт {p['vehicle']} починен."
    else:
        reply = "❌ У вас нет транспорта."
elif text.startswith("создать союз"):
    name = text.replace("создать союз", "").strip()
    soups[name] = [uid]
    p["squad"] = name
    reply = f"🛡️ Создан союз: {name}"
elif text.startswith("вступить союз"):
    name = text.replace("вступить союз", "").strip()
    if name in soups:
        soups[name].append(uid)
        p["squad"] = name
        reply = f"🤝 Вы вступили в союз: {name}"
    else:
        reply = "❌ Союз не найден."
elif text == "союз":
    reply = f"🛡️ Союз: {p['squad'] or 'нет'}"
elif text == "рейд":
    if p["squad"]:
        reward = random.randint(5, 15)
        p["resources"] += reward
        reply = f"⚔️ Рейд завершён. Награда: {reward} ресурсов."
    else:
        reply = "❌ Вы не в союзе."
elif text == "вскрыть":
    p["components"] += 1
    reply = "🧪 Образец вскрыт. Найден компонент."
elif text == "поиск":
    res = random.choice(resources)
    p["inventory"].append(res)
    reply = f"🔍 Найден ресурс: {res}"
elif text.startswith("использовать"):
    item = text.replace("использовать", "").strip()
    if item in p["inventory"]:
        p["inventory"].remove(item)
        reply = f"🩸 Использовано: {item}"
    else:
        reply = f"❌ У вас нет {item}"
elif text == "синтез":
    if p["components"] >= 3:
        p["inventory"].append("вакцина")
        p["components"] -= 3
        reply = "🔬 Вакцина синтезирована."
    else:
        reply = "❌ Нужно 3 компонента."
elif text == "магазин":
    reply = "🛒 Магазин:\n" + "\n".join(f"{k} — {v['cost']} ресурсов" for k, v in shop_items.items())
elif text.startswith("вызов") and "@" in text:
    target = text.split("@")[1]
    pvp_duels[uid] = target
    reply = f"⚔️ Вызов отправлен игроку @{target}"
elif text == "принять":
    target_uid = next((k for k, v in pvp_duels.items() if v == uname), None)
    if target_uid:
        reply = "🛡️ Дуэль началась. Используйте 'удар' или 'защита'"
    else:
        reply = "❌ Вызовов на вас нет."
elif text == "удар":
    p["hp"] -= 20
    reply = "💥 Удар! -20 HP противнику."
elif text == "защита":
    p["hp"] += 10
    reply = "🛡️ Защита активирована. +10 HP."
else:
    reply = "🤖 Неизвестная команда. Напиши /помощь"

await message.answer(reply)
await new_earning(message)

def register_handlers(dp: Dispatcher): dp.register_message_handler(biowar_handler, lambda m: m.text and m.chat.type in ['private', 'supergroup'])

MODULE_DESCRIPTION = { 'name': '🧬 Биовойна', 'description': 'Модуль с торговлей, транспортом, союзами, рейдами и боевой системой' }

