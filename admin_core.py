from aiogram import types, Router, F
from aiogram.types import Message
from aiogram.filters import Command
import time

router = Router()

# Хранилища
user_data = {}
admin_chat_id = None
hiscoin_balance = {}
last_farm_time = {}
user_ranks = {}

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
@router.message(Command("установить", "установить админ чат"))
async def set_admin_chat(message: Message):
    global admin_chat_id
    admin_chat_id = message.chat.id
    await message.reply("✅ Админ-чат установлен.")

# Репорт
@router.message(Command("репорт"))
async def report_handler(message: Message):
    if not admin_chat_id:
        return await message.reply("❌ Админ-чат не настроен.")
    await message.reply("⏳ Репорт отправлен.")
    await message.bot.send_message(
        admin_chat_id,
        f"⚠️ Репорт от @{message.from_user.username or message.from_user.id}:\n{message.text}"
    )

# Вызов администрации
@router.message(F.text.lower().in_(["админ", "позвать админа", "позвать админов"]))
async def call_admin(message: Message):
    await message.reply("📢 Вызван администратор!")

@router.message(F.text.lower() == "позвать зга")
async def call_zga(message: Message):
    await message.reply("👩‍✈️ Вызван заместитель главной админши!")

@router.message(F.text.lower().in_(["позвать владельца", "позвать еву"]))
async def call_owner(message: Message):
    await message.reply("👑 Вызван владелец проекта — Ева!")

# Команда .ping
@router.message(F.text == ".ping")
async def ping_passthrough(message: Message):
    await message.reply("✅ Я тут!")

# Ответ на "бот"
@router.message(F.text.lower() == "бот")
async def bot_react(message: Message):
    await message.reply("🤖 Я здесь, слушаю тебя!")

# Википедия — заглушка
@router.message(Command("википедия"))
async def wikipedia_search(message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not query:
        return await message.reply("❌ Укажи запрос: `википедия <запрос>`")
    # Здесь мог бы быть реальный ответ, но мы работаем без библиотеки
    await message.reply(f"🔎 Статья по запросу: \"{query}\"\n(⚠️ Ответ сгенерирован ботом — модуль Wikipedia отключён)")

# Праздник
@router.message(F.text == "!праздник")
async def fix_holiday(message: Message):
    try:
        await message.pin()
        await message.reply("🎉 Праздник закреплён!")
    except:
        await message.reply("❌ Нет прав на закрепление сообщений.")

# Фарм Hiscoin
@router.message(Command("фарм"))
async def farm_command(message: Message):
    uid = message.from_user.id
    now = time.time()
    if uid in last_farm_time and now - last_farm_time[uid] < 180:
        return await message.reply("⏳ Подожди 3 минуты между фармом.")

    hiscoin_balance[uid] = hiscoin_balance.get(uid, 0) + 10
    last_farm_time[uid] = now
    await message.reply("💰 Ты получил 10 Hiscoin!")

# Баланс
@router.message(Command("мешок"))
async def check_balance(message: Message):
    uid = message.from_user.id
    balance = hiscoin_balance.get(uid, 0)
    await message.reply(f"🎒 У тебя {balance} Hiscoin.")

# +ранг (по реплаю)
@router.message(Command("+ранг"))
async def set_rank(message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Используй в ответ на сообщение.")
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажи номер ранга.")
    try:
        rank = int(args[1])
    except ValueError:
        return await message.reply("❌ Номер ранга должен быть числом.")
    if rank == 10 and message.from_user.username != "Ева":
        return await message.reply("🚫 Только Ева может выдать 10-й ранг.")
    user_ranks[message.reply_to_message.from_user.id] = rank
    await message.reply(f"✅ Ранг установлен: {rank_titles.get(rank, str(rank))}")

# -ранг (по реплаю)
@router.message(Command("-ранг"))
async def downgrade_rank(message: Message):
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

# /ранг — показать свой ранг
@router.message(Command("ранг"))
async def my_rank(message: Message):
    uid = message.from_user.id
    rank = user_ranks.get(uid, 0)
    title = rank_titles.get(rank, "Без ранга")
    await message.reply(f"🎖️ Твой ранг: {title} ({rank})")
