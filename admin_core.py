import json, time, os
from datetime import datetime
from aiogram import types, Dispatcher

OWNER_ID = 8174117949
OWNER_USERNAME = "NEWADA_Night"

# === Путь к базам ===
BALANCE_FILE = "hiscoin_balance.json"
RANK_FILE = "user_ranks.json"
REPORT_FILE = "reports.json"

# === Хранилища ===
admin_chat_id = None
last_farm_time = {}
hiscoin_balance = {}
user_ranks = {str(OWNER_ID): 10}
reports = []

rank_titles = {
    1: "★ Рядовой", 2: "☆ Ефрейтор", 3: "⚔️ Капрал", 4: "⚡ Сержант",
    5: "🏛️ Лейтенант", 6: "💪 Майор", 7: "🛡️ Полковник",
    8: "🌋 Генерал", 9: "💫 Главнокомандующий", 10: "🔥 Владыка войны"
}

# === Загрузка / Сохранение ===
def save_data():
    with open(BALANCE_FILE, "w") as f: json.dump(hiscoin_balance, f)
    with open(RANK_FILE, "w") as f: json.dump(user_ranks, f)
    with open(REPORT_FILE, "w") as f: json.dump(reports, f)

def load_data():
    global hiscoin_balance, user_ranks, reports
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f: hiscoin_balance = json.load(f)
    if os.path.exists(RANK_FILE):
        with open(RANK_FILE, "r") as f: user_ranks = json.load(f)
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r") as f: reports = json.load(f)

# === Админ-чат ===
async def set_admin_chat(message: types.Message):
    global admin_chat_id
    admin_chat_id = message.chat.id
    await message.reply("✅ Админ-чат установлен.")

# === Репорт ===
async def report_handler(message: types.Message):
    if not admin_chat_id:
        return await message.reply("❌ Админ-чат не настроен.")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_text = message.text.strip()
    username = message.from_user.username or message.from_user.full_name
    entry = {
        "user_id": message.from_user.id,
        "username": username,
        "report": report_text,
        "datetime": now
    }
    reports.append(entry)
    save_data()
    msg = f"⚠️ Репорт от @{username}\n🕒 {now}\n📄 {report_text}"
    await message.bot.send_message(admin_chat_id, msg)
    try:
        await message.bot.send_message(OWNER_ID, msg)
    except:
        pass
    await message.reply("⏳ Репорт отправлен.")

# === Фарм Hiscoin ===
async def farm_command(message: types.Message):
    uid = str(message.from_user.id)
    now = time.time()
    if uid in last_farm_time and now - last_farm_time[uid] < 180:
        return await message.reply("⏳ Подожди 3 минуты между фармом.")
    hiscoin_balance[uid] = hiscoin_balance.get(uid, 0) + 10
    last_farm_time[uid] = now
    save_data()
    await message.reply("💰 Ты получил 10 Hiscoin!")

# === Баланс ===
async def check_balance(message: types.Message):
    uid = str(message.from_user.id)
    balance = hiscoin_balance.get(uid, 0)
    await message.reply(f"🎒 У тебя {balance} Hiscoin.")

# === Топ Hiscoin ===
async def top_hiscoin(message: types.Message):
    if not hiscoin_balance:
        return await message.reply("📉 Никто ещё не фармил.")
    sorted_users = sorted(hiscoin_balance.items(), key=lambda x: x[1], reverse=True)[:10]
    result = "🏆 Топ Hiscoin:\n"
    for i, (uid, score) in enumerate(sorted_users, 1):
        rank = user_ranks.get(uid, 0)
        result += f"{i}. ID: {uid} — {score} 💰 (Ранг: {rank_titles.get(rank, '—')})\n"
    await message.reply(result)

# === +ранг ===
async def set_rank(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Используй в ответ на сообщение.")
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажи номер ранга.")
    try:
        rank = int(args[1])
    except ValueError:
        return await message.reply("❌ Номер ранга должен быть числом.")
    if rank == 10 and message.from_user.id != OWNER_ID:
        return await message.reply("🚫 Только владелец может выдать 10-й ранг.")
    user_ranks[str(message.reply_to_message.from_user.id)] = rank
    save_data()
    await message.reply(f"✅ Ранг установлен: {rank_titles.get(rank, str(rank))}")

# === -ранг ===
async def downgrade_rank(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Используй в ответ на сообщение.")
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажи число понижения.")
    try:
        rank = int(args[1])
    except ValueError:
        return await message.reply("❌ Укажи число понижения.")
    target_id = str(message.reply_to_message.from_user.id)
    current = user_ranks.get(target_id, 0)
    if current <= rank:
        user_ranks[target_id] = 0
        save_data()
        return await message.reply("❌ Ранг снят. Игрок исключён из рейтинга.")
    user_ranks[target_id] = current - rank
    save_data()
    await message.reply(f"📉 Ранг понижен до: {rank_titles.get(user_ranks[target_id], user_ranks[target_id])}")

# === /ранг ===
async def my_rank(message: types.Message):
    uid = str(message.from_user.id)
    rank = user_ranks.get(uid, 0)
    title = rank_titles.get(rank, "Без ранга")
    await message.reply(f"🎖️ Твой ранг: {title} ({rank})")

# === Регистрация ===
def register_handlers(dp: Dispatcher):
    load_data()
    dp.register_message_handler(set_admin_chat, lambda m: m.text.lower().startswith("установить админ"))
    dp.register_message_handler(report_handler, lambda m: m.text.lower().startswith("репорт"))
    dp.register_message_handler(farm_command, lambda m: m.text.lower() == "фарм")
    dp.register_message_handler(check_balance, lambda m: m.text.lower() == "мой мешок")
    dp.register_message_handler(top_hiscoin, lambda m: m.text.lower() == "топ hiscoin")
    dp.register_message_handler(set_rank, lambda m: m.text.lower().startswith("+ранг"))
    dp.register_message_handler(downgrade_rank, lambda m: m.text.lower().startswith("-ранг"))
    dp.register_message_handler(my_rank, lambda m: m.text.lower() == "ранг")
