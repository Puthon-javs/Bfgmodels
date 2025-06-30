from aiogram import types, Dispatcher import time, json, os from datetime import datetime

=== Владелец ===

OWNER_ID = 8174117949 OWNER_USERNAME = "NEWADA_Night"

=== Хранилища ===

DATA_FILE = "hiscoin_data.json" REPORTS_FILE = "reports.json"

def load_data(): if os.path.exists(DATA_FILE): with open(DATA_FILE, "r") as f: data = json.load(f) else: data = { "hiscoin_balance": {}, "last_farm_time": {}, "user_ranks": {str(OWNER_ID): 10} } return data

def save_data(): with open(DATA_FILE, "w") as f: json.dump(data, f)

def load_reports(): if os.path.exists(REPORTS_FILE): with open(REPORTS_FILE, "r") as f: return json.load(f) return []

def save_reports(): with open(REPORTS_FILE, "w") as f: json.dump(reports, f)

data = load_data() reports = load_reports()

admin_chat_id = None rank_titles = { 1: "★ Рядовой", 2: "☆ Ефрейтор", 3: "⚔️ Капрал", 4: "⚡ Сержант", 5: "🏛️ Лейтенант", 6: "💪 Майор", 7: "🛡️ Полковник", 8: "🌋 Генерал", 9: "💫 Главнокомандующий", 10: "🔥 Владыка войны" }

=== Команды ===

async def set_admin_chat(message: types.Message): global admin_chat_id admin_chat_id = message.chat.id await message.reply("✅ Админ-чат установлен.")

async def report_handler(message: types.Message): global reports if not admin_chat_id: return await message.reply("❌ Админ-чат не настроен.") reason = message.text.replace("репорт", "", 1).strip() if not reason: return await message.reply("❗ Укажи причину репорта.")

now = datetime.now().strftime("%d.%m.%Y %H:%M")
entry = {
    "user_id": message.from_user.id,
    "username": message.from_user.username,
    "reason": reason,
    "datetime": now
}
reports.append(entry)
save_reports()

text = f"📅 {now.split()[0]} 🕒 {now.split()[1]}\n⚠️ Причина: {reason}\n👤 От: @{message.from_user.username}"
await message.bot.send_message(admin_chat_id, text)
try:
    await message.bot.send_message(OWNER_ID, text)
except:
    pass

async def view_reports(message: types.Message): if not reports: return await message.reply("📭 Репортов нет.") msg = "\n\n".join([f"📅 {r['datetime']}\n⚠️ {r['reason']}\n👤 @{r['username']}" for r in reports[-10:]]) await message.reply(f"📋 Последние репорты:\n\n{msg}")

async def call_admin(message: types.Message): await message.reply("📢 Вызван администратор!")

async def call_admins(message: types.Message): await message.reply("📢 Вызваны администраторы!")

async def call_zga(message: types.Message): await message.reply("👩‍✈️ Вызван заместитель главной админши!")

async def call_owner(message: types.Message): await message.reply(f"👑 Вызван владелец проекта — @{OWNER_USERNAME}!") try: await message.bot.send_message(OWNER_ID, f"🚨 Вызов от @{message.from_user.username} в чате {message.chat.title or message.chat.id}") except: pass

async def ping_passthrough(message: types.Message): pass

async def bot_react(message: types.Message): await message.reply("🤖 Я здесь, слушаю тебя!")

async def fix_holiday(message: types.Message): try: await message.pin() await message.reply("🎉 Праздник закреплён!") except: await message.reply("❌ Нет прав на закрепление сообщений.")

async def farm_command(message: types.Message): uid = str(message.from_user.id) now = time.time() if uid in data["last_farm_time"] and now - data["last_farm_time"][uid] < 180: return await message.reply("⏳ Подожди 3 минуты между фармом.") data["hiscoin_balance"][uid] = data["hiscoin_balance"].get(uid, 0) + 10 data["last_farm_time"][uid] = now save_data() await message.reply("💰 Ты получил 10 Hiscoin!")

async def check_balance(message: types.Message): uid = str(message.from_user.id) balance = data["hiscoin_balance"].get(uid, 0) await message.reply(f"🎒 У тебя {balance} Hiscoin.")

async def top_hiscoin(message: types.Message): top = sorted(data["hiscoin_balance"].items(), key=lambda x: x[1], reverse=True)[:10] result = "🥇 Топ Hiscoin:\n" for i, (uid, coins) in enumerate(top, 1): name = f"<a href="tg://user?id={uid}">Пользователь</a>" result += f"{i}. {name} — {coins}\n" await message.reply(result, parse_mode="HTML")

async def set_rank(message: types.Message): if not message.reply_to_message: return await message.reply("⚠️ Используй в ответ на сообщение.") args = message.text.split() if len(args) < 2: return await message.reply("❌ Укажи номер ранга.") try: rank = int(args[1]) except ValueError: return await message.reply("❌ Номер ранга должен быть числом.") if rank == 10 and message.from_user.id != OWNER_ID: return await message.reply("🚫 Только владелец может выдать 10-й ранг.") uid = str(message.reply_to_message.from_user.id) data["user_ranks"][uid] = rank save_data() await message.reply(f"✅ Ранг установлен: {rank_titles.get(rank, str(rank))}")

async def downgrade_rank(message: types.Message): if not message.reply_to_message: return await message.reply("⚠️ Используй в ответ на сообщение.") args = message.text.split() if len(args) < 2: return await message.reply("❌ Укажи число понижения.") try: rank = int(args[1]) except ValueError: return await message.reply("❌ Укажи число понижения.") target_id = str(message.reply_to_message.from_user.id) current = data["user_ranks"].get(target_id, 0) if current <= rank: data["user_ranks"][target_id] = 0 save_data() return await message.reply("❌ Ранг снят. Игрок исключён из рейтинга.") data["user_ranks"][target_id] = current - rank save_data() await message.reply(f"📉 Ранг понижен до: {rank_titles.get(data['user_ranks'][target_id], data['user_ranks'][target_id])}")

async def my_rank(message: types.Message): uid = str(message.from_user.id) rank = data["user_ranks"].get(uid, 0) title = rank_titles.get(rank, "Без ранга") await message.reply(f"🎖️ Твой ранг: {title} ({rank})")

=== Регистрация хендлеров ===

def register_handlers(dp: Dispatcher): dp.register_message_handler(set_admin_chat, commands=["установить", "установить_админ_чат"]) dp.register_message_handler(report_handler, lambda m: m.text.lower().startswith("репорт")) dp.register_message_handler(view_reports, commands=["просмотр_репортов"]) dp.register_message_handler(call_admin, lambda m: m.text.lower() == "позвать админа") dp.register_message_handler(call_admins, lambda m: m.text.lower() == "позвать админов") dp.register_message_handler(call_zga, lambda m: m.text.lower() == "позвать зга") dp.register_message_handler(call_owner, lambda m: m.text.lower() in ["позвать владельца", "позвать еву"]) dp.register_message_handler(ping_passthrough, lambda m: m.text == ".ping") dp.register_message_handler(bot_react, lambda m: m.text.lower() == "бот") dp.register_message_handler(fix_holiday, lambda m: m.text == "!праздник") dp.register_message_handler(farm_command, lambda m: m.text.lower() == "фарм") dp.register_message_handler(check_balance, lambda m: m.text.lower() == "мой мешок") dp.register_message_handler(top_hiscoin, lambda m: m.text.lower() == "топ hiscoin") dp.register_message_handler(set_rank, lambda m: m.text.startswith("+ранг")) dp.register_message_handler(downgrade_rank, lambda m: m.text.startswith("-ранг")) dp.register_message_handler(my_rank, lambda m: m.text.lower() == "ранг")

