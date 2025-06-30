from aiogram import types, Dispatcher from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery from commands.db import cursor, conn from assets.transform import transform_int as tr import random

uk_articles = [ {"number": 158, "title": "Кража", "text": "Тайное хищение чужого имущества."}, {"number": 228, "title": "Наркотики", "text": "Хранение наркотиков."}, {"number": 105, "title": "Убийство", "text": "Умышленное причинение смерти."}, {"number": 161, "title": "Грабёж", "text": "Открытое хищение имущества."}, {"number": 163, "title": "Вымогательство", "text": "Требование имущества под угрозой."} ]

DIFFICULTY = { "easy":    {"label": "🟢 Easy",    "exp": 1000,  "money": 500,   "fail": 0.1}, "normal":  {"label": "🟡 Normal",  "exp": 3000,  "money": 1000,  "fail": 0.25}, "medium":  {"label": "🟠 Medium",  "exp": 5000,  "money": 2000,  "fail": 0.4}, "hard":    {"label": "🔴 Hard",    "exp": 7000,  "money": 3000,  "fail": 0.6}, "brutal":  {"label": "⚫️ Brutal",  "exp": 10000, "money": 5000,  "fail": 0.8}, "dark":    {"label": "🩸 DARK RED", "exp": 25000, "money": 10000, "fail": 0.93} }

players = {}

STAGES = { 1: [("🔓 Вскрыть замок и выйти", 2), ("🧍 Подождать и наблюдать", 3), ("👊 Напасть на охранника", "fail")], 2: [("🚪 Выйти в коридор", 4), ("📞 Позвонить другу", "fail"), ("🔦 Спуститься в подвал", 5)], 3: [("💤 Охранник уснул — выйти!", 2), ("🪟 Вылезти через окно", 5), ("🔊 Поднять тревогу", "fail")], 4: [("🏃‍♂ Пробежать мимо камеры", 6), ("🔐 Вскрыть дверь с кодом", "fail"), ("🧍 Прятаться под носилками", 6)], 5: [("🔋 Взломать электрическую дверь", 6), ("🧱 Проломить стену", "fail"), ("🧴 Использовать масло и открыть люк", 6)], 6: [("🛥 Убежать на лодке", "win"), ("🚁 Захватить вертолёт", "win"), ("🚙 Угнать машину", "win"), ("🚶 Побежать в лес", "fail")] }

def next_stage_kb(uid): stage = players[uid]["stage"] kb = InlineKeyboardMarkup() for i, (label, ) in enumerate(STAGES.get(stage, []), 1): kb.add(InlineKeyboardButton(f"{i}. {label}", callback_data=f"prison_step{stage}_{i}")) return kb

async def start_escape(message: types.Message): kb = InlineKeyboardMarkup() for key, data in DIFFICULTY.items(): kb.add(InlineKeyboardButton(data["label"], callback_data=f"prison_start_{key}")) await message.answer("🏚 Выберите уровень сложности побега:", reply_markup=kb)

async def choose_difficulty(call: CallbackQuery): uid = call.from_user.id diff = call.data.split("_")[-1] article = random.choice(uk_articles) players[uid] = { "article": article, "difficulty": diff, "stage": 1 } await call.message.edit_text( f"📜 Статья {article['number']} — {article['title']} " f"{article['text']}

🔐 Побег начался... Выберите действие кнопкой или напишите цифру:", reply_markup=next_stage_kb(uid) )

async def process_step(call: CallbackQuery): uid = call.from_user.id data = call.data.split("_") if len(data) < 4: return await call.answer("❌ Ошибка данных кнопки.") stage = int(data[2]) index = int(data[3]) - 1 await handle_step(uid, call.message, stage, index, is_button=True)

async def process_step_text(message: types.Message): uid = message.from_user.id if uid not in players: return if not message.text.strip().isdigit(): return index = int(message.text.strip()) - 1 stage = players[uid]["stage"] await handle_step(uid, message, stage, index, is_button=False)

async def handle_step(uid, target, stage, index, is_button=True): try: if uid not in players or players[uid]["stage"] != stage: if is_button: await target.answer("⛔ Неактуальный ход.") return

actions = STAGES.get(stage)
    if not actions or index >= len(actions):
        if is_button:
            await target.answer("❌ Неверный выбор.")
        return

    label, result = actions[index]
    fail_chance = DIFFICULTY[players[uid]["difficulty"]]["fail"]

    if result == "fail" or random.random() < fail_chance:
        cursor.execute("UPDATE users SET escape_fails = escape_fails + 1 WHERE user_id = ?", (uid,))
        conn.commit()
        msg = "🚨 Вас поймали. Побег провален."
        del players[uid]
        return await target.edit_text(msg) if is_button else await target.reply(msg)

    if result == "win":
        diff = players[uid]["difficulty"]
        prize = DIFFICULTY[diff]
        cursor.execute("UPDATE users SET balance = balance + ?, exp = exp + ?, escape_wins = escape_wins + 1 WHERE user_id = ?",
                       (prize["money"], prize["exp"], uid))
        conn.commit()
        msg = f"🚪 Ты сбежал!\n🎁 +{tr(prize['money'])} монет, +{tr(prize['exp'])} опыта"
        del players[uid]
        return await target.edit_text(msg) if is_button else await target.reply(msg)

    players[uid]["stage"] = result
    msg = f"🔄 Этап {result} — выбери действие (или напиши 1, 2, 3):"
    return await target.edit_text(msg, reply_markup=next_stage_kb(uid)) if is_button else await target.reply(msg, reply_markup=next_stage_kb(uid))

except Exception as e:
    print(f"[ERROR] Побег: {e}")
    return await target.answer("❌ Ошибка при обработке.") if is_button else await target.reply("❌ Произошла ошибка.")

async def my_escape_stats(message: types.Message): uid = message.from_user.id cursor.execute("SELECT escape_wins, escape_fails FROM users WHERE user_id = ?", (uid,)) row = cursor.fetchone() if row: wins, fails = row await message.answer(f"📊 Твоя статистика побегов:\n✅ Побегов: {wins}\n❌ Провалов: {fails}")

async def top_escapers(message: types.Message): cursor.execute("SELECT user_id, escape_wins FROM users WHERE escape_wins > 0 ORDER BY escape_wins DESC LIMIT 5") rows = cursor.fetchall() results = [] for i, (uid, wins) in enumerate(rows, 1): try: user = await message.bot.get_chat(uid) name = user.first_name or user.username or f"ID {uid}" medal = "🏅" if wins >= 50 else "🥈" if wins >= 25 else "🥉" if wins >= 10 else "" link = f"<a href='tg://user?id={uid}'>{medal} {name}</a> — {wins} побед" results.append(link) except: results.append(f"{i}. ID {uid} — {wins} побед") await message.answer("🏆 Топ побегов:\n" + "\n".join(results), parse_mode="HTML")

def register_handlers(dp: Dispatcher): dp.register_message_handler(start_escape, lambda m: m.text.lower() == "побег") dp.register_callback_query_handler(choose_difficulty, lambda c: c.data.startswith("prison_start_")) dp.register_callback_query_handler(process_step, lambda c: c.data.startswith("prison_step_")) dp.register_message_handler(process_step_text, lambda m: m.from_user.id in players and m.text.isdigit()) dp.register_message_handler(my_escape_stats, lambda m: m.text.lower() == "мой побег") dp.register_message_handler(top_escapers, lambda m: m.text.lower() == "топ побегов")

