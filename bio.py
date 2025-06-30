from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import random

# Статьи УК
uk_articles = [
    {"number": 158, "title": "Кража", "text": "Тайное хищение чужого имущества."},
    {"number": 228, "title": "Наркотики", "text": "Хранение наркотических веществ."},
    {"number": 105, "title": "Убийство", "text": "Умышленное причинение смерти."},
    {"number": 161, "title": "Грабёж", "text": "Открытое хищение чужого имущества."},
    {"number": 163, "title": "Вымогательство", "text": "Требование имущества под угрозой."}
]

# Сложности и награды
DIFFICULTY = {
    "easy": {"label": "🟢 Easy", "exp": 1000, "money": 500},
    "normal": {"label": "🟡 Normal", "exp": 3000, "money": 1000},
    "hard": {"label": "🔴 Hard", "exp": 7000, "money": 3000},
    "dark": {"label": "🩸 DARK RED", "exp": 25000, "money": 10000}
}

# Игроки
players = {}

# Сцены (те же для всех, приз зависит от сложности)
scenes = {
    1: {
        "text": "👮 Охранник заснул у камеры. Что делать?\n1️⃣ Побежать\n2️⃣ Украсть ключ\n3️⃣ Ждать",
        "choices": {"1": 2, "2": 3, "3": 4}
    },
    2: {
        "text": "🚨 Ты выбежал, но наткнулся на охрану.\n1️⃣ Ударить\n2️⃣ Спрятаться",
        "choices": {"1": "caught", "2": 5}
    },
    3: {
        "text": "🗝 У тебя ключ! Что дальше?\n1️⃣ Открыть дверь\n2️⃣ Спрятать ключ",
        "choices": {"1": 5, "2": 4}
    },
    4: {
        "text": "⏳ Ты ждал слишком долго. Перевели в карцер. Конец.",
        "choices": {}
    },
    5: {
        "text": "🏃‍♂️ Побег удался! Ты на свободе!",
        "choices": {}
    },
    "caught": {
        "text": "🔒 Тебя поймали. Побег провалился.",
        "choices": {}
    }
}

# Команда /побег
async def show_difficulty(message: types.Message):
    kb = InlineKeyboardMarkup()
    for key, data in DIFFICULTY.items():
        kb.add(InlineKeyboardButton(data["label"], callback_data=f"pb_start_{key}"))
    await message.answer("🎮 Выберите уровень сложности:", reply_markup=kb)

# Нажал кнопку
async def start_game_callback(call: CallbackQuery):
    uid = call.from_user.id
    diff_key = call.data.split("_")[-1]
    diff_data = DIFFICULTY.get(diff_key)

    if not diff_data:
        await call.answer("Ошибка выбора.")
        return

    article = random.choice(uk_articles)
    players[uid] = {
        "article": article,
        "scene": 1,
        "difficulty": diff_key
    }

    await call.message.edit_text(
        f"📜 Статья: {article['number']} — {article['title']}\n"
        f"{article['text']}\n\n"
        f"🧱 Уровень: {diff_data['label']}\n\n"
        f"{scenes[1]['text']}"
    )

# Продолжение игры
async def continue_game(message: types.Message):
    uid = message.from_user.id
    if uid not in players:
        return

    choice = message.text.strip()
    player = players[uid]
    current = player["scene"]
    scene = scenes.get(current)

    if not scene or choice not in scene["choices"]:
        await message.answer("❌ Неверный выбор. Напиши: 1, 2 или 3.")
        return

    next_scene = scene["choices"][choice]
    if isinstance(next_scene, str):  # "caught"
        reward = DIFFICULTY[player["difficulty"]]
        await message.answer(
            f"{scenes[next_scene]['text']}\n\n"
            f"🎁 Награда: 0 опыта, 0 монет"
        )
        del players[uid]
        return

    next_text = scenes[next_scene]["text"]
    player["scene"] = next_scene
    if not scenes[next_scene]["choices"]:
        reward = DIFFICULTY[player["difficulty"]]
        success = (next_scene == 5)
        result = next_text
        if success:
            result += f"\n\n🎁 Награда: {reward['exp']} опыта, {reward['money']} монет"
        else:
            result += f"\n\n🎁 Награда: 500 опыта (мораль), 0 монет"
        await message.answer(result)
        del players[uid]
    else:
        await message.answer(next_text)

# Регистрация
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_difficulty, lambda m: m.text.lower() == "побег")
    dp.register_callback_query_handler(start_game_callback, lambda c: c.data.startswith("pb_start_"))
    dp.register_message_handler(continue_game, lambda m: m.from_user.id in players and m.text.isdigit())
