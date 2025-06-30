from aiogram import types, Dispatcher from aiogram.dispatcher.filters import Text from aiogram.types import Message from datetime import datetime import asyncio import json import os

📂 Файл базы данных

DB_FILE = "admin_module_data.json" OWNER_ID = 8174117949  # Заменить на твой ID
DB_FILE = "admin_module_data.json" OWNER_USERNAME = "NEWADA_Night"

📦 Загрузка/сохранение базы

def load_db(): if os.path.exists(DB_FILE): with open(DB_FILE, "r") as f: return json.load(f) return {"hiscoin": {}, "ranks": {}, "reports": []}

def save_db(data): with open(DB_FILE, "w") as f: json.dump(data, f, indent=2)

📊 Инициализация

DB = load_db() CD_USERS = set()

📌 Команды администраций

async def call_admins(msg: Message): await msg.answer("🛡️ Вызов администрации... Ожидайте! 🔔")

async def call_zga(msg: Message): await msg.answer("🔰 Заместитель Главной Админши уже в пути!")

async def call_owner(msg: Message): await msg.answer("👑 Владелец призван на место!")

async def call_eva(msg: Message): await msg.answer("👩‍💻 Владелец (Ева) уведомлена!")

📜 Репорты

async def report_handler(msg: Message): if not msg.reply_to_message: return await msg.reply("Ответьте на сообщение, чтобы отправить репорт") DB['reports'].append({ "from": msg.from_user.id, "to": msg.reply_to_message.from_user.id, "reason": msg.text, "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }) save_db(DB) await msg.reply("📝 Репорт отправлен")

async def view_reports(msg: Message): if not DB['reports']: return await msg.reply("📭 Репортов нет") text = "📜 Репорты:\n" for r in DB['reports'][-10:]: text += f"🕒 {r['datetime']}\n🎯 ID цели: {r['to']}\n📖 Причина: {r['reason']}\n\n" await msg.answer(text)

🪙 Фарм Hiscoin

async def farm_handler(msg: Message): uid = str(msg.from_user.id) if uid in CD_USERS: return await msg.reply("⏳ Подожди 3 минуты") CD_USERS.add(uid) DB['hiscoin'][uid] = DB['hiscoin'].get(uid, 0) + 1 save_db(DB) await msg.reply("💸 +1 Hiscoin") await asyncio.sleep(180) CD_USERS.remove(uid)

async def show_balance(msg: Message): uid = str(msg.from_user.id) coins = DB['hiscoin'].get(uid, 0) await msg.reply(f"💰 У тебя {coins} Hiscoin")

async def show_top(msg: Message): top = sorted(DB['hiscoin'].items(), key=lambda x: x[1], reverse=True)[:10] text = "📈 Топ Hiscoin:\n" for i, (uid, amt) in enumerate(top, 1): text += f"{i}. {uid} — {amt}🪙\n" await msg.reply(text)

🧱 Ранги

async def add_rank(msg: Message): if not msg.reply_to_message: return await msg.reply("Нужно ответить на сообщение") if msg.from_user.id != OWNER_ID and '10' in msg.text: return await msg.reply("❌ Только владелец может назначить 10 ранг") uid = str(msg.reply_to_message.from_user.id) rank = msg.text.split()[-1] DB['ranks'][uid] = int(rank) save_db(DB) await msg.reply(f"✅ Ранг {rank} установлен")

async def remove_rank(msg: Message): if not msg.reply_to_message: return await msg.reply("Нужно ответить на сообщение") uid = str(msg.reply_to_message.from_user.id) if uid in DB['ranks']: DB['ranks'][uid] -= 1 if DB['ranks'][uid] <= 0: del DB['ranks'][uid] save_db(DB) await msg.reply("⬇️ Ранг понижен")

async def show_rank_admins(msg: Message): if not DB['ranks']: return await msg.reply("Нет админов") text = "👥 Админы по рангам:\n" for uid, rank in DB['ranks'].items(): text += f"👤 {uid} — Ранг {rank}\n" await msg.reply(text)

🎉 Праздник

async def prazdnik(msg: Message): await msg.answer("🎉 Сегодня праздник! Поздравляем всех!")

👥 Список админов

async def all_admins(msg: Message): if not DB['ranks']: return await msg.reply("Нет админов") text = "📋 Все админы:\n" for uid in DB['ranks']: text += f"👤 ID: {uid}\n" await msg.reply(text)

🔍 Мой ID

async def my_id(msg: Message): await msg.reply(f"🆔 Твой ID: {msg.from_user.id}")

📎 Регистрация

def register_handlers(dp: Dispatcher): dp.register_message_handler(report_handler, Text(equals="репорт")) dp.register_message_handler(view_reports, Text(equals="репорты")) dp.register_message_handler(farm_handler, Text(equals="фарма")) dp.register_message_handler(show_balance, Text(equals=["мешок", "мой мешок"])) dp.register_message_handler(show_top, Text(equals="топ hiscoin")) dp.register_message_handler(add_rank, Text(startswith="+ранг")) dp.register_message_handler(remove_rank, Text(startswith="-ранг")) dp.register_message_handler(show_rank_admins, Text(equals="ранг админы")) dp.register_message_handler(call_admins, Text(equals=["админ", "позвать админов"])) dp.register_message_handler(call_zga, Text(equals="позвать зга")) dp.register_message_handler(call_owner, Text(equals="позвать владельца")) dp.register_message_handler(call_eva, Text(equals="позвать еву")) dp.register_message_handler(prazdnik, Text(equals=["!праздник", "!празник"])) dp.register_message_handler(all_admins, Text(equals=["админы", ".админы", "!админы"])) dp.register_message_handler(my_id, Text(equals="мой ид"))

