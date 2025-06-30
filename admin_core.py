admin_core.py

from aiogram import types, Router, F from aiogram.types import Message from aiogram.utils.markdown import hbold from aiogram.filters import Command import time import wikipedia

router = Router()

Хранилище

user_data = {} admin_chat_id = None hiscoin_balance = {} last_farm_time = {} user_ranks = {} rank_titles = { 1: "\u2605 Рядовой", 2: "\u2606 Ефрейтор", 3: "\u2694\ufe0f Капрал", 4: "\u26a1 Сержант", 5: "\ud83c\udfdb\ufe0f Лейтенант", 6: "\ud83d\udcaa Майор", 7: "\ud83d\udee1\ufe0f Полковник", 8: "\ud83c\udf0b Генерал", 9: "\ud83d\udcab Главнокомандующий", 10: "\ud83d\udd25 Владыка войны" }

Админ чат установка

@router.message(Command("установить", "установить админ чат")) async def set_admin_chat(message: Message): global admin_chat_id admin_chat_id = message.chat.id await message.reply("✅ Админ-чат установлен.")

Репорт

@router.message(Command("репорт")) async def report_handler(message: Message): if not admin_chat_id: return await message.reply("❌ Админ-чат не настроен.") await message.reply("⏳ Репорт отправлен.") await message.bot.send_message(admin_chat_id, f"⚠️ Репорт от @{message.from_user.username}:\n{message.text}")

Вызов администрации

@router.message(F.text.lower().in_(["админ", "позвать админа", "позвать админов"])) async def call_admin(message: Message): await message.reply("📢 Вызван администратор!")

@router.message(F.text.lower() == "позвать зга") async def call_zga(message: Message): await message.reply("👩‍✈️ Вызван заместитель главной админши!")

@router.message(F.text.lower().in_(["позвать владельца", "позвать еву"])) async def call_owner(message: Message): await message.reply("👑 Вызван владелец проекта — Ева!")

Википедия

@router.message(Command("википедия")) async def wikipedia_search(message: Message): query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None if not query: return await message.reply("❌ Укажи запрос: википедия <запрос>") try: wikipedia.set_lang("ru") summary = wikipedia.summary(query, sentences=2) await message.reply(f"🔎 {hbold(query)}:\n{summary}") except Exception as e: await message.reply("❌ Не удалось найти статью.")

Праздник

@router.message(F.text == "!праздник") async def fix_holiday(message: Message): try: await message.pin() await message.reply("🎉 Праздник закреплён!") except: await message.reply("❌ Нет прав на закрепление сообщений.")

Ping auto-reply

@router.message(F.text == ".ping") async def auto_ping(message: Message): await message.reply("🏓 pong")

Ответ на слово "бот"

@router.message(F.text.lower() == "бот") async def bot_react(message: Message): await message.reply("🤖 Я здесь, слушаю тебя!")

Фарм Hiscoin

@router.message(Command("фарм")) async def farm_command(message: Message): uid = message.from_user.id now = time.time() if uid in last_farm_time and now - last_farm_time[uid] < 180: return await message.reply("⏳ Подожди 3 минуты между фармом.")

hiscoin_balance[uid] = hiscoin_balance.get(uid, 0) + 10
last_farm_time[uid] = now
await message.reply("💰 Ты получил 10 Hiscoin!")

+ранг

@router.message(Command("+ранг")) async def set_rank(message: Message): if not message.reply_to_message: return await message.reply("⚠️ Используй в ответ на сообщение.") args = message.text.split() if len(args) < 2: return await message.reply("❌ Укажи номер ранга.") rank = int(args[1]) if rank == 10 and message.from_user.username != "Ева": return await message.reply("🚫 Только Ева может выдать 10-й ранг.") user_ranks[message.reply_to_message.from_user.id] = rank await message.reply(f"✅ Ранг установлен: {rank_titles.get(rank, str(rank))}")

-ранг

@router.message(Command("-ранг")) async def downgrade_rank(message: Message): if not message.reply_to_message: return await message.reply("⚠️ Используй в ответ на сообщение.") args = message.text.split() if len(args) < 2: return await message.reply("❌ Укажи номер для понижения.") rank = int(args[1]) target_id = message.reply_to_message.from_user.id current = user_ranks.get(target_id, 0) if current <= rank: user_ranks[target_id] = 0 return await message.reply("❌ Ранг снят. Игрок исключён из рейтинга.") user_ranks[target_id] = current - rank await message.reply(f"📉 Ранг понижен до: {rank_titles.get(user_ranks[target_id], user_ranks[target_id])}")

