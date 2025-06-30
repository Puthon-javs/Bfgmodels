# -- coding: utf-8 --

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
import json, time, os, random

# === НАСТРОЙКИ ===
OWNER_ID = 8174117949
OWNER_USERNAME = "@NEWADA_Night"
DATABASE_PATH = "admin_module_db.json"

# === ЗАГРУЗКА / СОХРАНЕНИЕ БД ===
def load_db():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admins": [], "zga": [], "reports": [], "balance": {}, "ranks": {}, "admin_chat": None}

def save_db():
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# === ПЕРЕМЕННЫЕ ===
db = load_db()
cooldowns = {}

# === ХЭЛПЕРЫ ===
def is_admin(user_id):
    return user_id in db["admins"] or user_id in db["zga"] or user_id == OWNER_ID

def send_report(text):
    target = db.get("admin_chat") or OWNER_ID
    return [types.Message.to_object({'chat': {'id': target}, 'text': text})]

# === РЕГИСТРАЦИЯ КОМАНД ===
def register_handlers(dp: Dispatcher):

    @dp.message_handler(commands=['мой', 'мой id'])
    async def my_id(msg: Message):
        if 'id' in msg.text:
            await msg.reply(f"🧾 Твой Telegram ID: {msg.from_user.id}")

    @dp.message_handler(lambda m: m.text and m.text.lower().startswith("установить админ чат"))
    async def set_admin_chat(msg: Message):
        if msg.from_user.id != OWNER_ID:
            return
        db["admin_chat"] = msg.chat.id
        save_db()
        await msg.reply("✅ Этот чат теперь админ-центр.")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "админы")
    async def list_admins(msg: Message):
        admins = "\n".join([f"👮 {aid}" for aid in db["admins"]])
        zga = "\n".join([f"🧠 {zid}" for zid in db["zga"]])
        owner = f"👑 {OWNER_ID} ({OWNER_USERNAME})"
        await msg.reply(f"👥 Админы:\n{admins or '—'}\n\n🧠 ЗГА:\n{zga or '—'}\n\n{owner}")

    @dp.message_handler(lambda m: m.text and m.text.startswith("репорт "))
    async def handle_report(msg: Message):
        report = msg.text[7:].strip()
        db['reports'].append({"from": msg.from_user.id, "text": report})
        save_db()
        for rmsg in send_report(f"🚨 Репорт от {msg.from_user.id}:\n{report}"):
            await msg.bot.send_message(rmsg.chat.id, rmsg.text)
        await msg.reply("✅ Репорт отправлен.")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "репорты")
    async def show_reports(msg: Message):
        if msg.from_user.id != OWNER_ID:
            return
        last = db['reports'][-10:]
        if not last:
            await msg.reply("Нет жалоб.")
            return
        text = "📣 Последние репорты:\n\n" + "\n\n".join([f"{r['from']}: {r['text']}" for r in last])
        await msg.reply(text)

    @dp.message_handler(lambda m: m.text and m.text.lower() in ["позвать админа", "позвать админов"])
    async def call_admin(msg: Message):
        for aid in db["admins"]:
            await msg.bot.send_message(aid, f"🚨 Вызов админа из чата {msg.chat.id} от {msg.from_user.id}")
        await msg.reply("👮‍♂️ Админы уведомлены.")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "позвать зга")
    async def call_zga(msg: Message):
        for zid in db["zga"]:
            await msg.bot.send_message(zid, f"🧠 Вызов ЗГА из чата {msg.chat.id} от {msg.from_user.id}")
        await msg.reply("🧠 ЗГА уведомлены.")

    @dp.message_handler(lambda m: m.text and m.text.lower() in ["позвать владельца", "позвать еву"])
    async def call_owner(msg: Message):
        await msg.bot.send_message(OWNER_ID, f"👑 Вызов владельца из чата {msg.chat.id} от {msg.from_user.id}")
        await msg.reply("👑 Владелец уведомлён.")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "фарма")
    async def farm(msg: Message):
        uid = str(msg.from_user.id)
        now = time.time()
        if uid in cooldowns and now - cooldowns[uid] < 180:
            return await msg.reply("⏳ Подожди немного.")
        cooldowns[uid] = now
        db['balance'][uid] = db['balance'].get(uid, 0) + 10
        save_db()
        await msg.reply("💰 Ты получил 10 Hiscoin!")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "мой мешок")
    async def my_bag(msg: Message):
        uid = str(msg.from_user.id)
        bal = db['balance'].get(uid, 0)
        await msg.reply(f"💼 В твоем мешке {bal} Hiscoin")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "топ хис")
    async def top_hiscoin(msg: Message):
        data = sorted(db['balance'].items(), key=lambda x: x[1], reverse=True)[:10]
        text = "🏆 Топ Hiscoin:\n"
        for i, (uid, val) in enumerate(data, 1):
            text += f"{i}. {uid}: {val} 💰\n"
        await msg.reply(text)

    @dp.message_handler(lambda m: m.reply_to_message and m.text.startswith("+ранг "))
    async def increase_rank(msg: Message):
        if not is_admin(msg.from_user.id): return
        try:
            n = int(msg.text.split()[1])
            uid = str(msg.reply_to_message.from_user.id)
            db['ranks'][uid] = min(10, db['ranks'].get(uid, 0) + n)
            save_db()
            await msg.reply(f"✅ Ранг повышен до {db['ranks'][uid]}")
        except:
            await msg.reply("⚠️ Ошибка.")

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
        except:
            await msg.reply("⚠️ Ошибка.")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "ранг")
    async def show_rank(msg: Message):
        uid = str(msg.from_user.id)
        rank = db['ranks'].get(uid, 0)
        await msg.reply(f"🎖️ Твой ранг: {rank}")

    @dp.message_handler(lambda m: m.text and m.text.startswith("википедия "))
    async def wikipedia_query(msg: Message):
        query = msg.text.split(" ", 1)[1]
        await msg.reply(f"🔍 Wikipedia: {query} (результат заглушен)")

    @dp.message_handler(lambda m: m.text and m.text.lower() == "!праздник")
    async def pin_fest(msg: Message):
        await msg.pin()
        await msg.reply("📌 Праздник закреплён!")

    @dp.message_handler(lambda m: m.text and m.text == ".ping")
    async def auto_ping(msg: Message):
        await msg.reply("🏓 Я здесь!")

    @dp.message_handler(lambda m: m.text and "бот" in m.text.lower())
    async def pretty_bot_reply(msg: Message):
        phrases = ["Я здесь, милорд!", "Ваш бот к услугам.", "Готов выполнять приказы."]
        await msg.reply(random.choice(phrases))
