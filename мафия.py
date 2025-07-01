TRUE MAFIA BOT (FSM-ЛОГИКА, РОЛИ, ГОЛОСОВАНИЕ, БЕЗ ТОКЕНА)

from aiogram import Bot, Dispatcher, types from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton from aiogram.contrib.fsm_storage.memory import MemoryStorage from aiogram.dispatcher import FSMContext from aiogram.dispatcher.filters.state import State, StatesGroup import asyncio, random

API_TOKEN = ""  # токен не требуется, оставь пустым или вставь вручную при запуске

bot = Bot(token=API_TOKEN) dp = Dispatcher(bot, storage=MemoryStorage())

Игровые состояния

class MafiaStates(StatesGroup): waiting_for_players = State() night_phase = State() day_vote = State()

players = {}  # {user_id: {"name": str, "role": str, "alive": bool}} game_chat_id = None

ROLES = [ "🤵🏻 Дон", "🤵🏼 Мафия", "🕵️‍ Комиссар", "👮🏼‍♂️ Сержант", "👨🏼‍⚕️ Доктор", "🔪 Маньяк", "👨🏼 Мирный житель", "💃🏼 Любовница", "👨🏼‍💼 Адвокат", "🤦🏼‍♂️ Самоубийца", "🧙🏼‍♂️ Бомж", "🤞 Счастливчик", "💣 Камикадзе" ]

РЕГИСТРАЦИЯ ИГРОКОВ

@dp.message_handler(commands=['start_game']) async def start_game(msg: types.Message, state: FSMContext): global players, game_chat_id game_chat_id = msg.chat.id players = {} await state.set_state(MafiaStates.waiting_for_players.state) await msg.answer("🎲 Игра начинается! Напиши /join чтобы участвовать.")

@dp.message_handler(commands=['join'], state=MafiaStates.waiting_for_players) async def join(msg: types.Message): if msg.from_user.id not in players: players[msg.from_user.id] = {"name": msg.from_user.full_name, "role": None, "alive": True} await msg.answer(f"✅ {msg.from_user.full_name} присоединился к игре.")

@dp.message_handler(commands=['begin'], state=MafiaStates.waiting_for_players) async def begin(msg: types.Message, state: FSMContext): if len(players) < 3: await msg.answer("⚠️ Нужно минимум 3 игрока.") return

assigned = random.sample(ROLES, len(players))
for user_id, role in zip(players, assigned):
    players[user_id]["role"] = role
    try:
        await bot.send_message(user_id, f"🎭 Ты - {role}!")
    except:
        await msg.answer(f"⚠️ Не удалось отправить роль {players[user_id]['name']}, он должен быть в боте.")

await state.set_state(MafiaStates.night_phase.state)
await msg.answer("🌃 Наступает ночь. Игроки делают действия...")
await asyncio.sleep(10)

# Заглушка: никто не умирает
await state.set_state(MafiaStates.day_vote.state)
await msg.answer("🏙 Утро наступило. Все живы. Голосование началось.")
await show_voting()

ГОЛОСОВАНИЕ

async def show_voting(): keyboard = InlineKeyboardMarkup() for uid, p in players.items(): if p['alive']: keyboard.add(InlineKeyboardButton(p['name'], callback_data=f"vote:{uid}")) await bot.send_message(game_chat_id, "🗳️ Кого линчевать?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("vote:"), state=MafiaStates.day_vote) async def process_vote(call: types.CallbackQuery, state: FSMContext): victim_id = int(call.data.split(":")[1]) players[victim_id]['alive'] = False await call.message.edit_text(f"🔪 Линчевали: {players[victim_id]['name']} ({players[victim_id]['role']})")

# ПРОВЕРКА ПОБЕДЫ
await check_victory()
await state.set_state(MafiaStates.night_phase.state)
await bot.send_message(game_chat_id, "🌃 Наступает новая ночь...")

async def check_victory(): alive = [p for p in players.values() if p['alive']] mafia = [p for p in alive if "Мафия" in p['role'] or "Дон" in p['role']] civilians = [p for p in alive if "Мафия" not in p['role'] and "Дон" not in p['role']] if not mafia: await bot.send_message(game_chat_id, "👨🏼 Победа мирных!") return if len(mafia) >= len(civilians): await bot.send_message(game_chat_id, "🤵🏻 Победа мафии!") return

if name == 'main': from aiogram import executor executor.start_polling(dp, skip_updates=True)

