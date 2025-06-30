from aiogram import types
from aiogram.dispatcher import Dispatcher
import random
import time

# 🔐 Замените на свой Telegram user_id
ADMIN_ID = 8174117949

# 📊 Статистика
stats = {
    "команды": 0,
    "шутки": 0,
    "комплименты": 0,
    "ответы_ботяра": 0,
    "обзывалки": 0,
    "пользователи": set()
}

# 📘 Настоящие статьи УК РФ
uk_articles = [
    {
        "number": 105,
        "title": "Убийство",
        "text": "Умышленное причинение смерти другому человеку — наказывается лишением свободы от 6 до 15 лет."
    },
    {
        "number": 158,
        "title": "Кража",
        "text": "Тайное хищение чужого имущества — наказывается штрафом или лишением свободы до 2 лет."
    },
    {
        "number": 159,
        "title": "Мошенничество",
        "text": "Хищение имущества путём обмана или злоупотребления доверием."
    },
    {
        "number": 228,
        "title": "Наркотики",
        "text": "Незаконное приобретение и хранение наркотических средств — наказывается лишением свободы до 10 лет."
    }
]

# ==================== ФУНКЦИИ ====================

async def start(message: types.Message):
    stats["команды"] += 1
    stats["пользователи"].add(message.from_user.id)
    await message.answer("привет")


async def botyara(message: types.Message):
    stats["команды"] += 1
    stats["ответы_ботяра"] += 1
    stats["пользователи"].add(message.from_user.id)

    responses = [
        "Я тут 😊", "На месте 👍", "Работает 💻", "Чего звал? 🤖",
        "Готов к командам! 🔧", "Слушаю, командир! 🫡", "Ботяра в деле 😎",
        "Как всегда, рядом 💬", "Да-да, я вас понял! 📡", "На связи! 📱"
    ]
    await message.reply(random.choice(responses))


async def who_am_i(message: types.Message):
    stats["команды"] += 1
    stats["комплименты"] += 1
    stats["пользователи"].add(message.from_user.id)

    compliments = [
        "Ты невероятная! 💖", "Ты как солнце 🌞", "Ты просто космос! 🚀",
        "Таких, как ты, больше нет 😍", "Ты — красота и ум 💡💋",
        "Твоя улыбка — магия ✨", "Ты как вдохновение на весь день ☀️",
        "Ты словно песня 🎵", "Ты достойна всего самого прекрасного 🌷",
        "Ты — как редкое сокровище 💎"
    ]
    await message.reply(random.choice(compliments))


async def how_are_you(message: types.Message):
    stats["команды"] += 1
    stats["пользователи"].add(message.from_user.id)

    replies = [
        "Отлично! А у тебя как? 😊", "Живу, работаю 🤖",
        "Лучше всех 🙏", "С тобой настроение лучше 🌟",
        "Жду новых команд! 🛠️"
    ]
    await message.reply(random.choice(replies))


async def joke(message: types.Message):
    stats["команды"] += 1
    stats["шутки"] += 1
    stats["пользователи"].add(message.from_user.id)

    jokes = [
        "Почему программисты не любят природу? Там баги 🐛",
        "— Бот, ты живой? — Я поток 😁",
        "Как зовут поющего программиста? — АлгоритМихаил 🎤",
        "Ты как капча — раздражаешь 😤",
        "Упал сервер — встал DevOps 😅"
    ]
    await message.reply(random.choice(jokes))


async def ping(message: types.Message):
    start = time.perf_counter()
    reply = await message.reply("⏱️ Измеряю пинг...")
    end = time.perf_counter()

    ping_ms = round((end - start) * 1000, 2)
    await reply.edit_text(f"📡 Пинг: <b>{ping_ms} мс</b>", parse_mode="HTML")

    stats["команды"] += 1
    stats["пользователи"].add(message.from_user.id)


async def sk_reply(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Эту команду нужно использовать в ответ на чьё-то сообщение! 🙃")
        return

    stats["команды"] += 1
    stats["обзывалки"] += 1
    stats["пользователи"].add(message.from_user.id)

    insults = [
        "Ты как Wi-Fi в метро — вроде есть, но толку ноль 📶",
        "Гений... только наоборот 😏",
        "Если бы глупость светилась — ты был бы Солнцем 🌞",
        "Сложная личность... как регулярка на питоне 😵",
        "Тебя бы в логах найти и удалить 🧹"
    ]

    await message.reply_to_message.reply(random.choice(insults))
    try:
        await message.delete()
    except:
        pass


async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У тебя нет доступа к статистике 🔒")
        return

    total_users = len(stats["пользователи"])
    text = (
        f"📊 <b>Статистика бота</b>:\n"
        f"👥 Пользователей: <b>{total_users}</b>\n"
        f"📥 Команд: <b>{stats['команды']}</b>\n"
        f"💬 Ботяра: <b>{stats['ответы_ботяра']}</b>\n"
        f"💖 Комплименты: <b>{stats['комплименты']}</b>\n"
        f"🤣 Шутки: <b>{stats['шутки']}</b>\n"
        f"🧨 Обзывалки: <b>{stats['обзывалки']}</b>"
    )
    await message.reply(text, parse_mode="HTML")


async def show_status(message: types.Message):
    start = time.perf_counter()
    temp_msg = await message.reply("⏳ Собираю данные...")
    end = time.perf_counter()

    ping_ms = round((end - start) * 1000, 2)
    total_users = len(stats["пользователи"])

    text = (
        f"📊 <b>Статус бота</b>:\n"
        f"📡 Пинг: <b>{ping_ms} мс</b>\n"
        f"👥 Пользователей: <b>{total_users}</b>\n"
        f"📥 Команд: <b>{stats['команды']}</b>"
    )
    await temp_msg.edit_text(text, parse_mode="HTML")

    stats["команды"] += 1
    stats["пользователи"].add(message.from_user.id)


async def my_article(message: types.Message):
    stats["команды"] += 1
    stats["пользователи"].add(message.from_user.id)

    article = random.choice(uk_articles)
    article_text = (
        f"<b>УК РФ — Статья {article['number']}</b>\n"
        f"<b>{article['title']}</b>\n\n"
        f"{article['text']}"
    )
    await message.reply(article_text, parse_mode="HTML")


# ==================== РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ====================

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, lambda m: m.text.lower().startswith('привет'))
    dp.register_message_handler(botyara, lambda m: m.text.lower().startswith('ботяра'))
    dp.register_message_handler(who_am_i, lambda m: m.text.lower().startswith('я кто'))
    dp.register_message_handler(how_are_you, lambda m: m.text.lower().startswith('как дела'))
    dp.register_message_handler(joke, lambda m: m.text.lower().startswith('шутка'))
    dp.register_message_handler(sk_reply, lambda m: m.text.lower() == 'ск')
    dp.register_message_handler(ping, lambda m: m.text.lower() in ['ping', '.ping', '!ping', 'пинг', '.пинг', '!пинг'])
    dp.register_message_handler(show_stats, lambda m: m.text.lower() == 'статистика')
    dp.register_message_handler(show_status, lambda m: m.text.lower() == 'покажи')
    dp.register_message_handler(my_article, lambda m: m.text.lower() == 'моя статья')
