-- coding: utf-8 --

from aiogram import types from aiogram.dispatcher import Dispatcher from aiogram.types import Message import json, time, os, random, datetime

=== НАСТРОЙКИ ===

OWNER_ID = 8174117949 OWNER_USERNAME = "@NEWADA_Night" DATABASE_PATH = "admin_module_db.json"

=== ЗАГРУЗКА / СОХРАНЕНИЕ БД ===

def load_db(): if os.path.exists(DATABASE_PATH): with open(DATABASE_PATH, "r") as f: return json.load(f) return {"admins": [], "zga": [], "reports": [], "balance": {}, "ranks": {}, "admin_chat": None}

def save_db(): with open(DATABASE_PATH, "w") as f: json.dump(db, f)

=== ПЕРЕМЕННЫЕ ===

db = load_db() cooldowns = {}

=== ХЭЛПЕРЫ ===

def is_admin(user_id): return user_id in db["admins"] or user_id in db["zga"] or user_id == OWNER_ID

def get_rank_emoji(rank): emojis = ["❌", "🥄", "🥉", "🥈", "🥇", "🎖", "🏅", "⭐️", "🔥", "👑"] return emojis[min(rank, len(emojis)-1)]

=== РЕГИСТРАЦИЯ КОМАНД ===

def register_handlers(dp: Dispatcher):

@dp.message_handler(commands=['мой', 'мой id'])
async def my_id(msg: Message):
    await msg.reply(f"🧾 Твой Telegram ID: {msg.from_user.id}")

@dp.message_handler(lambda m: m.text and m.text.lower().startswith("установить админ чат"))
async def set_admin_chat(msg: Message):
    if msg.from_user.id != OWNER_ID: return
    db["admin_chat"] = msg.chat.id
    save_db()
    await msg.reply("✅ Этот чат теперь админ-центр.")

@dp.message_handler(lambda m: m.text.lower() == "админы")
async def list_admins(msg: Message):
    lines = []
    for uid in db["admins"]:
        r = db["ranks"].get(str(uid), 0)
        lines.append(f"👮‍♂️ {uid} {get_rank_emoji(r)} (ранг {r})")
    for uid in db["zga"]:
        r = db["ranks"].get(str(uid), 0)
        lines.append(f"🧠 {uid} {get_rank_emoji(r)} (ЗГА ранг {r})")
    lines.append(f"👑 {OWNER_ID} ({OWNER_USERNAME})")
    await msg.reply("👥 Админский состав:\n" + "\n".join(lines))

@dp.message_handler(lambda m: m.text.lower() == "владелец")
async def show_owner(msg: Message):
    await msg.reply(f"👑 Владелец: {OWNER_ID} ({OWNER_USERNAME})")

@dp.message_handler(lambda m: m.reply_to_message and m.text.lower() == "+админ")
async def give_admin(msg: Message):
    if msg.from_user.id != OWNER_ID: return
    uid = msg.reply_to_message.from_user.id
    if uid not in db["admins"]:
        db["admins"].append(uid)
        save_db()
        await msg.reply("✅ Админ выдан.")

@dp.message_handler(lambda m: m.reply_to_message and m.text.lower() == "-админ")
async def remove_admin(msg: Message):
    if msg.from_user.id != OWNER_ID: return
    uid = msg.reply_to_message.from_user.id
    if uid in db["admins"]:
        db["admins"].remove(uid)
        save_db()
        await msg.reply("⚠️ Админ снят.")

@dp.message_handler(lambda m: m.reply_to_message and m.text.startswith("+ранг "))
async def increase_rank(msg: Message):
    if not is_admin(msg.from_user.id): return
    try:
        n = int(msg.text.split()[1])
        uid = str(msg.reply_to_message.from_user.id)
        db['ranks'][uid] = min(10, db['ranks'].get(uid, 0) + n)
        save_db()
        await msg.reply(f"✅ Ранг повышен до {db['ranks'][uid]}")
    except: pass

@dp.message_handler(lambda m: m.reply_to_message and m.text.startswith("-ранг "))
async def decrease_rank(msg: Message):
    if not is_admin(msg.from_user.id): return
    try:
        n = int(msg.text.split()[1])
        uid = str(msg.reply_to_message.from_user.id)
        db['ranks'][uid] = max(0, db['ranks'].get(uid, 0) - n)
        if db['ranks'][uid] == 0:
            db['ranks'].pop(uid)
        save_db()
        await msg.reply("⚠️ Ранг понижен.")
    except: pass

@dp.message_handler(lambda m: m.text.lower().startswith("репорт "))
async def handle_report(msg: Message):
    text = msg.text[7:].strip()
    if not text:
        return await msg.reply("❗ Укажи причину.")

    user_id = msg.from_user.id
    username = msg.from_user.username or "без username"
    full_link = f"<a href='tg://user?id={user_id}'>профиль</a>"

    reply_link = ""
    if msg.reply_to_message:
        chat_id = msg.chat.id
        msg_id = msg.reply_to_message.message_id
        reply_link = f"\n🔗 <a href='https://t.me/c/{str(chat_id)[4:]}/{msg_id}'>Ссылка на сообщение</a>" if str(chat_id).startswith("-100") else ""

    report = {
        "from": user_id,
        "text": text,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db["reports"].append(report)
    save_db()

    message_text = (
        f"🚨 <b>Новый репорт</b>\n"
        f"👤 {full_link} (@{username})\n"
        f"🕒 {report['time']}\n"
        f"📝 {report['text']}{reply_link}"
    )

    await msg.bot.send_message(OWNER_ID, message_text, parse_mode="HTML")

    if db.get("admin_chat"):
        await msg.bot.send_message(db["admin_chat"], message_text, parse_mode="HTML")

    await msg.reply("✅ Репорт отправлен.")

@dp.message_handler(lambda m: m.text.lower() == "репорты")
async def show_reports(msg: Message):
    if msg.from_user.id != OWNER_ID: return
    last = db['reports'][-10:]
    if not last:
        await msg.reply("📭 Репортов нет.")
    else:
        lines = [f"🗓 {r['time']}\n👤 {r['from']}\n📝 {r['text']}" for r in last]
        await msg.reply("📋 Последние репорты:\n\n" + "\n\n".join(lines))

