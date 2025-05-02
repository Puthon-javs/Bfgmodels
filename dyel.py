from aiogram import Dispatcher, types
from decimal import Decimal
from commands.db import conn as conngdb, cursor as cursorgdb
from assets.antispam import antispam, antispam_earning, new_earning_msg
from commands.main import win_luser
from assets.transform import transform_int as tr
import random

# Функция запуска дуэли
@antispam
async def duel_start(message: types.Message):
    user_id = message.from_user.id
    opponent_id = message.reply_to_message.from_user.id if message.reply_to_message else None

    if not opponent_id:
        await message.answer("Нужно ответить на сообщение пользователя, с которым хочешь сыграть!")
        return

    if opponent_id == user_id:
        await message.answer("Нельзя играть против себя!")
        return

    # Проверяем баланс инициатора
    initiator_balance = cursorgdb.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()
    if not initiator_balance or Decimal(initiator_balance[0]) < 100:
        await message.answer("У вас недостаточно средств (минимум 100 B-coins)!")
        return

    # Создаем клавиатуру для подтверждения дуэли
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Принять дуэль", callback_data=f"duel_accept|{user_id}|{opponent_id}"),
        types.InlineKeyboardButton("Отказаться", callback_data=f"duel_decline|{user_id}|{opponent_id}")
    )

    msg = await message.answer(
        f"🎯 {message.from_user.get_mention()} вызывает на дуэль {message.reply_to_message.from_user.get_mention()}!\n"
        f"Ставка: 100 B-coins\n"
        f"У вас есть 60 секунд чтобы принять вызов!",
        reply_markup=keyboard
    )
    await new_earning_msg(msg.chat.id, msg.message_id)

# Обработчик принятия дуэли
@antispam_earning
async def duel_accept(call: types.CallbackQuery):
    data = call.data.split('|')
    initiator_id = int(data[1])
    opponent_id = int(data[2])
    current_user = call.from_user.id

    if current_user != opponent_id:
        await call.answer("Этот вызов не для вас!", show_alert=True)
        return

    # Проверяем баланс оппонента
    opponent_balance = cursorgdb.execute('SELECT balance FROM users WHERE user_id = ?', (opponent_id,)).fetchone()
    if not opponent_balance or Decimal(opponent_balance[0]) < 100:
        await call.message.edit_text("У вас недостаточно средств для дуэли!")
        return

    # Проверяем баланс инициатора
    initiator_balance = cursorgdb.execute('SELECT balance FROM users WHERE user_id = ?', (initiator_id,)).fetchone()
    if not initiator_balance or Decimal(initiator_balance[0]) < 100:
        await call.message.edit_text("У инициатора дуэли недостаточно средств!")
        return

    # Снимаем ставки
    cursorgdb.execute('UPDATE users SET balance = balance - 100 WHERE user_id IN (?, ?)', (initiator_id, opponent_id))
    conngdb.commit()

    # Определяем победителя
    winner_id = random.choice([initiator_id, opponent_id])
    loser_id = opponent_id if winner_id == initiator_id else initiator_id

    # Начисляем выигрыш
    cursorgdb.execute('UPDATE users SET balance = balance + 200 WHERE user_id = ?', (winner_id,))
    conngdb.commit()

    # Получаем текущие балансы
    winner_balance = cursorgdb.execute('SELECT balance FROM users WHERE user_id = ?', (winner_id,)).fetchone()[0]
    loser_balance = cursorgdb.execute('SELECT balance FROM users WHERE user_id = ?', (loser_id,)).fetchone()[0]

    # Отправляем результат
    win_emoji, lose_emoji = await win_luser()
    await call.message.edit_text(
        f"{win_emoji} Победитель: {call.from_user.get_mention() if winner_id == current_user else f'user_{winner_id}'}\n"
        f"Выигрыш: 200 B-coins (100 + 100)\n\n"
        f"Баланс после дуэли:\n"
        f"Победитель: {tr(Decimal(winner_balance))} B-coins\n"
        f"Проигравший: {tr(Decimal(loser_balance))} B-coins",
        reply_markup=None
    )

# Обработчик отказа от дуэли
@antispam_earning
async def duel_decline(call: types.CallbackQuery):
    data = call.data.split('|')
    opponent_id = int(data[2])
    current_user = call.from_user.id

    if current_user != opponent_id:
        await call.answer("Этот вызов не для вас!", show_alert=True)
        return

    await call.message.edit_text(
        f"😐 {call.from_user.get_mention()} отказался от дуэли!",
        reply_markup=None
    )

# Функция регистрации хэндлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(duel_start, lambda message: message.text.lower().startswith('дуэль'))
    dp.register_callback_query_handler(duel_accept, text_startswith='duel_accept')
    dp.register_callback_query_handler(duel_decline, text_startswith='duel_decline')

# Описание модуля
MODULE_DESCRIPTION = {
    'name': '🎯 Дуэль',
    'description': (
        "Игра 'Дуэль' между пользователями\n"
        "Как играть:\n"
        "1. Ответьте на сообщение пользователя командой 'дуэль'\n"
        "2. Оппонент должен принять вызов\n"
        "3. Победитель получает 200 B-coins (100 от каждого)\n"
        "Минимальная ставка: 100 B-coins"
    )
}