from aiogram import types
from aiogram.dispatcher.filters import Command
import time

# Глобальные хранилища
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

def register_admin_handlers(dp):
    @dp.message_handler(commands=["установить", "установить_админ_чат"])
    async def set_admin_chat(message: types.Message):
        global admin_chat_id
        admin_chat_id = message.chat.id
        await message.reply("✅ Админ-чат установлен.")

    @dp.message_handler(commands=["репорт"])
    async def report_handler(message: types.Message):
        if not admin_chat_id:
            return await message.reply("❌ Админ-чат не настроен.")
        await message.reply("⏳ Репорт отправлен.")
        await message.bot.send_message(admin_chat_id, f"⚠️ Репорт от @{message.from_user.username}:\n{message.text}")

    @dp.message_handler(lambda msg: msg.text and msg.text.lower() in ["админ", "позвать админа", "позвать админов"])
    async def call_admin(message: types.Message):
        await message.reply("📢 Вызван администратор!")

    @dp.message_handler(lambda msg: msg.text and msg.text.lower() == "позвать зга")
    async def call_zga(message: types.Message):
        await message.reply("👩‍✈️ Вызван заместитель главной админши!")

    @dp.message_handler(lambda msg: msg.text and msg.text.lower() in ["позвать владельца", "позвать еву"])
    async def call_owner(message: types.Message):
        await message.reply("👑 Вызван владелец проекта — Ева!")

    @dp.message_handler(lambda msg: msg.text and msg.text.lower() == "бот")
    async def bot_react(message: types.Message):
        await message.reply("🤖 Я здесь, слушаю тебя!")

    @dp.message_handler(lambda msg: msg.text == "!праздник")
    async def fix_holiday(message: types.Message):
        try:
            await message.pin()
            await message.reply("🎉 Праздник закреплён!")
        except:
            await message.reply("❌ Нет прав на закрепление сообщений.")

    @dp.message_handler(commands=["фарм"])
    async def farm_command(message: types.Message):
        uid = message.from_user.id
        now = time.time()
        if uid in last_farm_time and now - last_farm_time[uid] < 180:
            return await message.reply("⏳ Подожди 3 минуты между фармом.")
        hiscoin_balance[uid] = hiscoin_balance.get(uid, 0) + 10
        last_farm_time[uid] = now
        await message.reply("💰 Ты получил 10 Hiscoin!")

    @dp.message_handler(commands=["мешок"])
    async def check_balance(message: types.Message):
        uid = message.from_user.id
        balance = hiscoin_balance.get(uid, 0)
        await message.reply(f"🎒 У тебя {balance} Hiscoin.")

    @dp.message_handler(commands=["+ранг"])
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
        if rank == 10 and message.from_user.username != "Ева":
            return await message.reply("🚫 Только Ева может выдать 10-й ранг.")
        user_ranks[message.reply_to_message.from_user.id] = rank
        await message.reply(f"✅ Ранг установлен: {rank_titles.get(rank, str(rank))}")

    @dp.message_handler(commands=["-ранг"])
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

    @dp.message_handler(commands=["ранг"])
    async def my_rank(message: types.Message):
        uid = message.from_user.id
        rank = user_ranks.get(uid, 0)
        title = rank_titles.get(rank, "Без ранга")
        await message.reply(f"🎖️ Твой ранг: {title} ({rank})")
