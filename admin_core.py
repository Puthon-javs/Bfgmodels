import json
import os
import time
from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

DATA_FILE = "admin_data.json"
OWNER_ID = 8174117949
OWNER_USERNAME = "@NEWADA_Night"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "admins": [],
            "zga": [],
            "hiscoin": {},
            "ranks": {},
            "admin_chat": None,
            "reports": []
        }, f)

with open(DATA_FILE, "r") as f:
    db = json.load(f)

def save_db():
    with open(DATA_FILE, "w") as f:
        json.dump(db, f)

cooldowns = {}

def is_owner(user_id: int):
    return user_id == OWNER_ID

@router.message(Command("установить админ чат"))
async def set_admin_chat(message: types.Message):
    if not is_owner(message.from_user.id):
        return
    db["admin_chat"] = message.chat.id
    save_db()
    await message.reply("✅ Установлен этот чат как админ-центр.")

@router.message(F.text.lower().startswith("репорт"))
async def report_admins(message: types.Message):
    text = message.text[6:].strip()
    if not text:
        await message.reply("⚠️ Укажи текст жалобы.")
        return
    db["reports"].append({"user": message.from_user.id, "text": text})
    db["reports"] = db["reports"][-10:]
    save_db()
    admin_chat = db.get("admin_chat")
    if admin_chat:
        await message.bot.send_message(admin_chat, f"🚨 Репорт от <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>:\n{text}")
    await message.reply("📨 Репорт отправлен.")

@router.message(Command("просмотр_репортов"))
async def show_reports(message: types.Message):
    if not is_owner(message.from_user.id):
        return
    if not db["reports"]:
        await message.reply("Нет репортов.")
        return
    text = "\n\n".join([f"👤 <code>{r['user']}</code>:\n{r['text']}" for r in db["reports"]])
    await message.reply(f"<b>📋 Последние репорты:</b>\n{text}")

@router.message(F.text.lower().in_([
    "позвать админа", "позвать админов", "позвать зга",
    "позвать владельца", "позвать еву", "админ", "админы", "зга", "ева"
]))
async def call_admins(message: types.Message):
    call_map = {
        "позвать админа": "📣 Вызов: обычный админ!",
        "позвать админов": "📣 Вызов: все админы, на связи!",
        "позвать зга": "📣 Вызов: заместитель главной админши!",
        "позвать владельца": f"📣 Вызов: {OWNER_USERNAME}, ты нужен здесь!",
        "позвать еву": f"📣 Вызов: {OWNER_USERNAME} (Ева), ты нужна!",
        "админ": "⚠️ Кто-то звал админа?",
        "админы": "⚠️ Вызываются админы...",
        "зга": "⚠️ Заместитель админа на подходе...",
        "ева": f"⚠️ @{OWNER_USERNAME} скоро будет здесь.",
    }
    await message.reply(call_map[message.text.lower()])

@router.message(F.text.lower() == "список админов")
async def list_admins(message: types.Message):
    text = "<b>📋 Список админов:</b>\n"
    text += f"👑 Владелец: <a href='tg://user?id={OWNER_ID}'>{OWNER_USERNAME}</a> — <code>{OWNER_ID}</code>\n\n"

    if db["zga"]:
        text += "🛡 ЗГА:\n"
        for uid in db["zga"]:
            text += f"• <a href='tg://user?id={uid}'>ID: {uid}</a>\n"
    else:
        text += "🛡 ЗГА: нет\n"

    if db["admins"]:
        text += "\n👨‍💻 Админы:\n"
        for uid in db["admins"]:
            text += f"• <a href='tg://user?id={uid}'>ID: {uid}</a>\n"
    else:
        text += "\n👨‍💻 Админов нет\n"

    await message.reply(text)

@router.message(F.text.lower() == "фарм")
async def farm(message: types.Message):
    user_id = str(message.from_user.id)
    now = time.time()
    if user_id in cooldowns and now - cooldowns[user_id] < 180:
        await message.reply("⌛ Жди 3 минуты перед следующим фармом.")
        return
    cooldowns[user_id] = now
    db["hiscoin"][user_id] = db["hiscoin"].get(user_id, 0) + 10
    save_db()
    await message.reply("💰 +10 Hiscoin!")

@router.message(F.text.lower() == "мой мешок")
async def my_bag(message: types.Message):
    user_id = str(message.from_user.id)
    coins = db["hiscoin"].get(user_id, 0)
    await message.reply(f"🎒 У тебя {coins} Hiscoin.")

@router.message(F.text.lower() == "топ hiscoin")
async def top_hiscoin(message: types.Message):
    if not db["hiscoin"]:
        await message.reply("Пока никто не фармил.")
        return
    sorted_users = sorted(db["hiscoin"].items(), key=lambda x: x[1], reverse=True)[:10]
    text = "<b>🏆 Топ Hiscoin:</b>\n"
    for i, (uid, coins) in enumerate(sorted_users, 1):
        text += f"{i}. <a href='tg://user?id={uid}'>ID {uid}</a> — {coins}💰\n"
    await message.reply(text)

@router.message(Command("ранг"))
async def show_rank(message: types.Message):
    user_id = str(message.from_user.id)
    rank = db["ranks"].get(user_id, 0)
    await message.reply(f"🏅 Твой ранг: {rank}")

@router.message(F.text.lower().startswith("+ранг"))
async def add_rank(message: types.Message):
    if not message.reply_to_message:
        await message.reply("⚠️ Ответь на сообщение пользователя.")
        return
    try:
        value = int(message.text.split()[1])
    except:
        await message.reply("⚠️ Укажи число ранга.")
        return
    user_id = str(message.reply_to_message.from_user.id)
    if value == 10 and not is_owner(message.from_user.id):
        await message.reply("❌ Только владелец может назначить 10 ранг.")
        return
    db["ranks"][user_id] = db["ranks"].get(user_id, 0) + value
    save_db()
    await message.reply(f"✅ Ранг пользователя обновлён: {db['ranks'][user_id]}")

@router.message(F.text.lower().startswith("-ранг"))
async def remove_rank(message: types.Message):
    if not message.reply_to_message:
        await message.reply("⚠️ Ответь на сообщение пользователя.")
        return
    try:
        value = int(message.text.split()[1])
    except:
        await message.reply("⚠️ Укажи число для понижения.")
        return
    user_id = str(message.reply_to_message.from_user.id)
    db["ranks"][user_id] = max(0, db["ranks"].get(user_id, 0) - value)
    if db["ranks"][user_id] == 0:
        del db["ranks"][user_id]
    save_db()
    await message.reply("⬇️ Ранг понижен.")

@router.message(F.text.lower().startswith("википедия"))
async def wikipedia(message: types.Message):
    query = message.text[9:].strip()
    if not query:
        await message.reply("⚠️ Введите запрос.")
        return
    await message.reply(f"🔍 <b>{query}</b> — (результат фейковый, заглушка).")

@router.message(F.text.lower() == "!праздник")
async def pin_holiday(message: types.Message):
    await message.pin()
    await message.reply("📌 Праздник закреплён!")

@router.message(F.text.lower() == ".ping")
async def ping_reply(message: types.Message):
    await message.reply("🏓 Пинг-понг, я на связи!")

@router.message(F.text.lower() == "бот")
async def bot_reply(message: types.Message):
    await message.reply("🤖 Я тут, красивый и готов помогать!")
