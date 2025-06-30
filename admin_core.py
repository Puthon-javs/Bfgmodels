from aiogram import types, Dispatcher
import time

# === Владелец ===
OWNER_ID = 8174117949  # 👈 Укажи свой user_id
OWNER_USERNAME = "NEWADA_Night"  # 👈 Укажи свой username без "@"

# Хранилища
user_data = {}
admin_chat_id = None
hiscoin_balance = {}
last_farm_time = {}
user_ranks = {OWNER_ID: 10}  # Владелец сразу получает 10 ранг

rank_titles = {
    1: "★ Рядовой",
    2: "☆ Ефрейтор",
    3: "⚔️ Капрал",
    4: "⚡ Сержант",
    5: "🏛️ Лейтенант",
    6: "💪 Майор",
    7: "🛡️ Полковник",
    8: "🌋 Генерал",
    9: "💫 Главнокомандующий",
    10: "🔥 Владыка войны"
}

# Установка админ-чата
async def set_admin_chat(message: types.Message):
    global admin_chat_id
    admin_chat_id = message.chat.id
    await message.reply("✅ Админ-чат установлен.")

# Репорт
async def report_handler(message: types.Message):
    if not admin_chat_id:
        return await message.reply("❌ Админ-чат не настроен.")
    await message.reply("⏳ Репорт отправлен.")
    await message.bot.send_message(admin_chat_id, f"⚠️ Репорт от @{message.from_user.username}:\n{message.text}")

# Вызов администрации
async def call_admin(message: types.Message):
    await message.reply("📢 Вызван администратор!")

async def call_zga(message: types.Message):
    await message.reply("👩‍✈️ Вызван заместитель главной админши!")

async def call_owner(message: types.Message):
    await message.reply(f"👑 Вызван владелец проекта — @{OWNER_USERNAME}!")
    try:
        await message.bot.send_message(OWNER_ID, f"🚨 Вызов от @{message.from_user.username} в чате {message.chat.title or message.chat.id}")
    except Exception as e:
        await message.reply("⚠️ Не удалось отправить сообщение владельцу (возможно, он заблокировал бота).")

# .ping
async def ping_passthrough(message: types.Message):
    pass

# Ответ на "бот"
async def bot_react(message: types.Message):
    await message.reply("🤖 Я здесь, слушаю тебя!")

# Праздник
async def fix_holiday(message: types.Message):
    try:
        await message.pin()
        await message.reply("🎉 Праздник закреплён!")
    except:
        await message.reply("❌ Нет прав на закрепление сообщений.")

# Фарм Hiscoin
async def farm_command(message: types.Message):
    uid = message.from_user.id
    now = time.time()
    if uid in last_farm_time and now - last_farm_time[uid] < 180:
        return await message.reply("⏳ Подожди 3 минуты между фармом.")
    hiscoin_balance[uid] = hiscoin_balance.get(uid, 0) + 10
    last_farm_time[uid] = now
    await message.reply("💰 Ты получил 10 Hiscoin!")

# Баланс
async def check_balance(message: types.Message):
    uid = message.from_user.id
    balance = hiscoin_balance.get(uid, 0)
    await message.reply(f"🎒 У тебя {balance} Hiscoin.")

# +ранг
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
    user_ranks[message.reply_to_message.from_user.id] = rank
    await message.reply(f"✅ Ранг установлен: {rank_titles.get(rank, str(rank))}")

# -ранг
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
    target_id = message.reply_to_message.from_user.id
    current = user_ranks.get(target_id, 0)
    if current <= rank:
        user_ranks[target_id] = 0
        return await message.reply("❌ Ранг снят. Игрок исключён из рейтинга.")
    user_ranks[target_id] = current - rank
    await message.reply(f"📉 Ранг понижен до: {rank_titles.get(user_ranks[target_id], user_ranks[target_id])}")

# /ранг
async def my_rank(message: types.Message):
    uid = message.from_user.id
    rank = user_ranks.get(uid, 0)
    title = rank_titles.get(rank, "Без ранга")
    await message.reply(f"🎖️ Твой ранг: {title} ({rank})")

# Регистрация всех хендлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(set_admin_chat, commands=["установить", "установить_админ_чат"])
    dp.register_message_handler(report_handler, commands=["репорт"])
    dp.register_message_handler(call_admin, lambda m: m.text.lower() in ["админ", "позвать админа", "позвать админов"])
    dp.register_message_handler(call_zga, lambda m: m.text.lower() == "позвать зга")
    dp.register_message_handler(call_owner, lambda m: m.text.lower() in ["позвать владельца", "позвать еву"])
    dp.register_message_handler(ping_passthrough, lambda m: m.text == ".ping")
    dp.register_message_handler(bot_react, lambda m: m.text.lower() == "бот")
    dp.register_message_handler(fix_holiday, lambda m: m.text == "!праздник")
    dp.register_message_handler(farm_command, commands=["фарм"])
    dp.register_message_handler(check_balance, commands=["мешок"])
    dp.register_message_handler(set_rank, commands=["+ранг"])
    dp.register_message_handler(downgrade_rank, commands=["-ранг"])
    dp.register_message_handler(my_rank, commands=["ранг"])
