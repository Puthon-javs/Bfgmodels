# -*- coding: utf-8 -*-

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import json, os, random, datetime

# === НАСТРОЙКИ ===
OWNER_ID = 8174117949
OWNER_USERNAME = "@NEWADA_Night"
DATABASE_PATH = "mafia_db.json"

# === РОЛИ ===
ROLES = [
    "👨🏼 Мирный житель",
    "🤵🏻 Дон",
    "🤵🏼 Мафия",
    "🕵️‍ Комиссар",
    "👮🏼‍♂️ Сержант",
    "👨🏼‍⚕️ Доктор",
    "🔪 Маньяк",
    "💃🏼 Любовница",
    "👨🏼‍💼 Адвокат",
    "🤦🏼‍♂️ Самоубийца",
    "🧙🏼‍♂️ Бомж",
    "🤞 Счастливчик",
    "💣 Камикадзе"
]

# === FSM ===
class GameState(StatesGroup):
    waiting_players = State()
    night_action = State()
    day_vote = State()
    end_game = State()

# === ЗАГРУЗКА / СОХРАНЕНИЕ БД ===
def load_db():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            return json.load(f)
    return {"players": {}, "stats": {}, "games": [], "admin_chat": None}

def save_db():
    with open(DATABASE_PATH, "w") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

db = load_db()
current_game = {"players": [], "roles": {}, "alive": [], "phase": "lobby", "votes": {}, "night_actions": {}, "day": 0}

# === ХЭЛПЕРЫ ===
def get_role(uid):
    return current_game["roles"].get(str(uid), "👨🏼 Мирный житель")

def is_alive(uid):
    return uid in current_game["alive"]

def mention(uid):
    return f'<a href="tg://user?id={uid}">{uid}</a>'

def assign_roles():
    players = current_game["players"]
    random.shuffle(players)
    roles_pool = ROLES.copy()
    random.shuffle(roles_pool)
    for uid in players:
        role = roles_pool.pop() if roles_pool else "👨🏼 Мирный житель"
        current_game["roles"][str(uid)] = role
        current_game["alive"].append(uid)

def check_victory():
    mafia = [uid for uid in current_game["alive"] if "маф" in get_role(uid).lower() or "дон" in get_role(uid).lower()]
    others = [uid for uid in current_game["alive"] if uid not in mafia]
    if not mafia:
        return "Мирные победили!"
    if len(mafia) >= len(others):
        return "Мафия победила!"
    return None

# === РЕГИСТРАЦИЯ КОМАНД ===
def register_handlers(dp: Dispatcher):

    @dp.message_handler(commands=["начать_мафию"])
    async def start_mafia(msg: Message):
        if msg.from_user.id != OWNER_ID:
            return await msg.reply("⛔ Только владелец может начать игру.")
        current_game["players"].clear()
        current_game["roles"].clear()
        current_game["alive"].clear()
        current_game["votes"].clear()
        current_game["night_actions"].clear()
        current_game["phase"] = "lobby"
        await msg.reply("🤵🏻 True Mafia:\nИгра начинается! Используй /войти чтобы присоединиться.")

    @dp.message_handler(commands=["войти"])
    async def join_game(msg: Message):
        uid = msg.from_user.id
        if current_game["phase"] != "lobby":
            return await msg.reply("❗ Игра уже идёт.")
        if uid not in current_game["players"]:
            current_game["players"].append(uid)
            await msg.reply("✅ Ты вошёл в игру.")
        else:
            await msg.reply("⛔ Ты уже в игре.")

    @dp.message_handler(commands=["начать_игру"])
    async def begin_game(msg: Message):
        if msg.from_user.id != OWNER_ID:
            return
        if len(current_game["players"]) < 3:
            return await msg.reply("❗ Нужно хотя бы 3 игрока.")
        assign_roles()
        for uid in current_game["players"]:
            role = get_role(uid)
            try:
                await msg.bot.send_message(uid, f"🎭 Твоя роль: <b>{role}</b>", parse_mode="HTML")
            except:
                pass
        current_game["phase"] = "night"
        current_game["day"] = 1
        await msg.reply("🌃 Наступает ночь.\nЖдите сообщений от бота в ЛС.")

    @dp.message_handler(commands=["живые"])
    async def alive_list(msg: Message):
        if not current_game["alive"]:
            return await msg.reply("😴 Никто не жив.")
        lines = [f"{i+1}. {mention(uid)}" for i, uid in enumerate(current_game["alive"])]
        await msg.reply("🧍 Живые:\n" + "\n".join(lines), parse_mode="HTML")

    @dp.message_handler(commands=["убить"])
    async def vote_kill(msg: Message):
        if current_game["phase"] != "day":
            return await msg.reply("⛔ Не время для голосования.")
        uid = msg.from_user.id
        if not is_alive(uid): return
        target_id = msg.reply_to_message.from_user.id if msg.reply_to_message else None
        if not target_id or target_id not in current_game["alive"]:
            return await msg.reply("❗ Ответь реплаем на живого игрока.")
        current_game["votes"][target_id] = current_game["votes"].get(target_id, 0) + 1
        await msg.reply(f"☑️ Голос принят за {mention(target_id)}", parse_mode="HTML")

    @dp.message_handler(commands=["голоса"])
    async def show_votes(msg: Message):
        if not current_game["votes"]:
            return await msg.reply("🗳 Пока никто не проголосовал.")
        lines = []
        for uid, count in current_game["votes"].items():
            lines.append(f"{mention(uid)} — {count} голос(ов)")
        await msg.reply("📊 Голоса:\n" + "\n".join(lines), parse_mode="HTML")

    @dp.message_handler(commands=["день"])
    async def start_day(msg: Message):
        if msg.from_user.id != OWNER_ID: return
        current_game["phase"] = "day"
        killed = []
        for uid, action in current_game["night_actions"].items():
            if action["type"] == "kill":
                killed.append(action["target"])
        if killed:
            for dead in killed:
                if dead in current_game["alive"]:
                    current_game["alive"].remove(dead)
            txt = "☀️ День наступает.\nПогибли:\n" + "\n".join([mention(uid) for uid in killed])
        else:
            txt = "☀️ День наступает.\nВсе выжили."
        await msg.reply(txt, parse_mode="HTML")
        current_game["night_actions"].clear()

        winner = check_victory()
        if winner:
            await msg.reply(f"🏁 Игра окончена: {winner}")
            current_game["phase"] = "ended"

    @dp.message_handler(commands=["ночь"])
    async def start_night(msg: Message):
        if msg.from_user.id != OWNER_ID: return
        current_game["phase"] = "night"
        await msg.reply("🌃 Ночь. Все роли выполняют свои действия в ЛС.")

    @dp.message_handler(commands=["репорт"])
    async def report(msg: Message):
        await msg.reply("📨 Чтобы отправить репорт, напиши: `репорт [причина]`", parse_mode="Markdown")

    @dp.message_handler(lambda m: m.text.lower().startswith("репорт "))
    async def handle_report(msg: Message):
        reason = msg.text[7:].strip()
        await msg.bot.send_message(OWNER_ID, f"🚨 Репорт от {mention(msg.from_user.id)}: {reason}", parse_mode="HTML")
        await msg.reply("✅ Репорт отправлен.")
