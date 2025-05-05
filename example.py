import asyncio
import random
import time
from decimal import Decimal

from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from assets.antispam import antispam, antispam_earning, new_earning
from assets.transform import transform_int as tr
from bot import bot
from commands.db import conn, cursor, url_name
from commands.help import CONFIG
from user import BFGuser, BFGconst

CONFIG['help_game'] += '\n   🔘 Дуэль [ставка] [реплай (опционально)]'


games = []
waiting = {}


def create_start_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="🤝 Принять дуэль", callback_data=f"duel-start"))
    return keyboard


async def update_balance(user_id: int, amount: int | str, operation="subtract") -> None:
    balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
    
    if operation == 'add':
        new_balance = Decimal(str(balance)) + Decimal(str(amount))
    else:
        new_balance = Decimal(str(balance)) - Decimal(str(amount))
    
    new_balance = "{:.0f}".format(new_balance)
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (str(new_balance), user_id))
    cursor.execute('UPDATE users SET games = games + 1 WHERE user_id = ?', (user_id,))
    conn.commit()


class Duel:
    def __init__(self, chat_id, user_id, summ, message_id, vs_bot=False, opponent_id=None):
        self.chat_id = chat_id
        self.user_id = user_id
        self.opponent_id = opponent_id
        self.vs_bot = vs_bot
        self.message_id = message_id
        self.summ = summ
        self.last_time = time.time()
        self.choices = {
            'user1_choice': None,
            'user2_choice': None
        }
        self.started = False
    
    async def start(self):
        self.started = True
        self.last_time = time.time()
        
        if self.vs_bot:
            text = f"🎮 {await url_name(self.user_id)} вызвал бота на дуэль!\n💰 Ставка: {tr(self.summ)}$\n\nВыберите ваш ход:"
            kb = self.get_choice_kb(self.user_id)
            await bot.edit_message_text(text, self.chat_id, self.message_id, reply_markup=kb)
        else:
            text = f"⚔️ {await url_name(self.user_id)} вызвал {await url_name(self.opponent_id)} на дуэль!\n💰 Ставка: {tr(self.summ)}$\n\nОжидаем ходы игроков..."
            await bot.edit_message_text(text, self.chat_id, self.message_id)
    
    def get_choice_kb(self, user_id):
        keyboard = InlineKeyboardMarkup(row_width=3)
        choices = ['✊', '✌️', '✋']
        
        # Для бота средняя сложность - иногда предсказуем, иногда нет
        if self.vs_bot and user_id != self.user_id:
            # Бот делает "умный" выбор с вероятностью 60%
            if random.random() < 0.6:
                user_choice = self.choices['user1_choice']
                if user_choice == '✊': bot_choice = '✋'
                elif user_choice == '✋': bot_choice = '✌️'
                else: bot_choice = '✊'
                return bot_choice
            else:
                return random.choice(choices)
        
        for choice in choices:
            keyboard.insert(InlineKeyboardButton(choice, callback_data=f"duel_choice_{choice}"))
        return keyboard
    
    async def make_choice(self, user_id, choice):
        if user_id == self.user_id:
            self.choices['user1_choice'] = choice
        else:
            self.choices['user2_choice'] = choice
        self.last_time = time.time()
        
        if self.vs_bot:
            bot_choice = self.get_choice_kb(self.user_id)  # Бот делает выбор
            self.choices['user2_choice'] = bot_choice
            await self.check_result()
        elif self.choices['user1_choice'] and self.choices['user2_choice']:
            await self.check_result()
        else:
            await bot.edit_message_text(
                f"⚔️ Дуэль между {await url_name(self.user_id)} и {await url_name(self.opponent_id)}\n💰 Ставка: {tr(self.summ)}$\n\n"
                f"Игроки делают выбор...\n"
                f"{await url_name(self.user_id)}: {'✅' if self.choices['user1_choice'] else '❌'}\n"
                f"{await url_name(self.opponent_id)}: {'✅' if self.choices['user2_choice'] else '❌'}",
                self.chat_id, self.message_id
            )
    
    async def check_result(self):
        choice1 = self.choices['user1_choice']
        choice2 = self.choices['user2_choice']
        
        # Определяем победителя
        if choice1 == choice2:
            result = "draw"
        elif (choice1 == '✊' and choice2 == '✌️') or \
             (choice1 == '✌️' and choice2 == '✋') or \
             (choice1 == '✋' and choice2 == '✊'):
            result = "user1"
        else:
            result = "user2"
        
        if result == "draw":
            text = f"🤝 Ничья!\n{choice1} vs {choice2}\n\nДеньги возвращены игрокам."
            await update_balance(self.user_id, self.summ, operation='add')
            if not self.vs_bot:
                await update_balance(self.opponent_id, self.summ, operation='add')
        elif result == "user1":
            winner = self.user_id
            loser = self.opponent_id if not self.vs_bot else "бот"
            text = f"🎉 {await url_name(winner)} побеждает!\n{choice1} бьёт {choice2}\n\nПриз: {tr(self.summ*2)}$"
            await update_balance(winner, self.summ*2, operation='add')
        else:
            winner = self.opponent_id if not self.vs_bot else "бот"
            loser = self.user_id
            text = f"🎉 {await url_name(winner) if not self.vs_bot else '🤖 Бот'} побеждает!\n{choice2} бьёт {choice1}\n\nПриз: {tr(self.summ*2)}$"
            if not self.vs_bot:
                await update_balance(winner, self.summ*2, operation='add')
        
        await bot.edit_message_text(text, self.chat_id, self.message_id)
        games.remove(self)


def find_waiting(chat_id, message_id):
    for game in waiting.keys():
        if game.chat_id == chat_id and game.message_id == message_id:
            return game
    return None


def find_game_by_mid(chat_id, message_id):
    for game in games:
        if game.chat_id == chat_id and game.message_id == message_id:
            return game
    return None


def find_game_by_userid(user_id):
    for game in games:
        if game.user_id == user_id or (hasattr(game, 'opponent_id') and game.opponent_id == user_id):
            return game
    return None


@antispam
async def start(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if find_game_by_userid(user.user_id):
        await message.answer(f'{user.url}, у вас уже есть активная игра {lose}')
        return
        
    try:
        if message.text.lower().split()[1] in ['все', 'всё']:
            summ = int(user.balance)
        else:
            summ = message.text.split()[1].replace('е', 'e')
            summ = int(float(summ))
    except:
        await message.answer(f'{user.url}, вы не ввели ставку для дуэли 🫤')
        return
    
    if summ < 10:
        await message.answer(f'{user.url}, минимальная ставка - 10$ {lose}')
        return
    
    if summ > int(user.balance):
        await message.answer(f'{user.url}, у вас недостаточно денег {lose}')
        return
    
    # Проверяем есть ли реплай
    opponent_id = None
    vs_bot = True
    
    if message.reply_to_message:
        opponent = message.reply_to_message.from_user
        if opponent.id == user.user_id:
            await message.answer(f'{user.url}, нельзя вызвать на дуэль самого себя {lose}')
            return
        if opponent.is_bot:
            await message.answer(f'{user.url}, нельзя вызвать на дуэль бота {lose}')
            return
        if int(BFGuser(opponent.id).balance) < summ:
            await message.answer(f'{user.url}, у пользователя недостаточно денег для такой ставки {lose}')
            return
        
        opponent_id = opponent.id
        vs_bot = False
    
    if vs_bot:
        msg = await message.answer(f"⚔️ {user.url} вызывает на дуэль бота!\n💰 Ставка: {tr(summ)}$\n\nПодготовка к дуэли...")
        game = Duel(msg.chat.id, user.user_id, summ, msg.message_id, vs_bot=True)
        games.append(game)
        await update_balance(user.user_id, summ, operation='subtract')
        await game.start()
    else:
        msg = await message.answer(f"⚔️ {user.url} вызывает на дуэль {await url_name(opponent_id)}!\n💰 Ставка: {tr(summ)}$\n\nОжидаю подтверждения...", 
                                 reply_markup=create_start_kb())
        game = Duel(msg.chat.id, user.user_id, summ, msg.message_id, vs_bot=False, opponent_id=opponent_id)
        waiting[game] = int(time.time()) + 180
        await update_balance(user.user_id, summ, operation='subtract')


@antispam_earning
async def start_game_kb(call: types.CallbackQuery, user: BFGuser):
    game = find_waiting(call.message.chat.id, call.message.message_id)
    
    if not game or user.user_id != game.opponent_id:
        return
    
    if int(user.balance) < game.summ:
        await bot.answer_callback_query(call.id, text='❌ У вас недостаточно денег.')
        return
    
    games.append(game)
    waiting.pop(game)
    await update_balance(user.user_id, game.summ, operation='subtract')
    await game.start()


@antispam_earning
async def make_choice_kb(call: types.CallbackQuery, user: BFGuser):
    game = find_game_by_mid(call.message.chat.id, call.message.message_id)
    
    if not game:
        return
    
    if user.user_id not in [game.user_id, game.opponent_id] and not game.vs_bot:
        await bot.answer_callback_query(call.id, '❌ Вы не участник этой дуэли.')
        return
    
    if game.vs_bot and user.user_id != game.user_id:
        await bot.answer_callback_query(call.id, '❌ Это дуэль с ботом, вы не можете участвовать.')
        return
    
    choice = call.data.split('_')[2]
    await game.make_choice(user.user_id, choice)
    await bot.answer_callback_query(call.id, text=f'✅ Вы выбрали: {choice}')


async def check_waiting():
    while True:
        for game, gtime in list(waiting.items()):
            if int(time.time()) > gtime:
                waiting.pop(game)
                chat_id = game.chat_id
                message_id = game.message_id
                try:
                    await bot.send_message(chat_id, f'❌ {await url_name(game.opponent_id)} не принял вызов. Деньги возвращены.', 
                                         reply_to_message_id=message_id)
                    await update_balance(game.user_id, game.summ, operation='add')
                except:
                    pass
        await asyncio.sleep(30)
        
        
async def check_game():
    while True:
        for game in games:
            if int(time.time()) > int(game.last_time+120):
                games.remove(game)
                chat_id = game.chat_id
                message_id = game.message_id
                try:
                    if game.vs_bot:
                        # В дуэли с ботом - если игрок не сделал выбор, бот побеждает
                        text = f'⚠️ Время на ход вышло!\n🤖 Бот побеждает по умолчанию.'
                        await update_balance(game.user_id, game.summ*2, operation='subtract')  # Возвращаем только ставку
                    else:
                        # Определяем кто не сделал выбор
                        if not game.choices['user1_choice'] and not game.choices['user2_choice']:
                            text = f'⚠️ Оба игрока не сделали выбор!\nДеньги возвращены.'
                            await update_balance(game.user_id, game.summ, operation='add')
                            await update_balance(game.opponent_id, game.summ, operation='add')
                        elif not game.choices['user1_choice']:
                            text = f'⚠️ {await url_name(game.user_id)} не сделал выбор!\n{await url_name(game.opponent_id)} побеждает.'
                            await update_balance(game.opponent_id, game.summ*2, operation='add')
                        else:
                            text = f'⚠️ {await url_name(game.opponent_id)} не сделал выбор!\n{await url_name(game.user_id)} побеждает.'
                            await update_balance(game.user_id, game.summ*2, operation='add')
                    
                    await bot.send_message(chat_id, text, reply_to_message_id=message_id)
                except:
                    pass
        await asyncio.sleep(30)


loop = asyncio.get_event_loop()
loop.create_task(check_waiting())
loop.create_task(check_game())


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, lambda message: message.text.lower().startswith('дуэль'))
    dp.register_callback_query_handler(start_game_kb, text_startswith='duel-start')
    dp.register_callback_query_handler(make_choice_kb, text_startswith='duel_choice')


MODULE_DESCRIPTION = {
    'name': '⚔️ Дуэль',
    'description': 'Камень-ножницы-бумага на деньги. Можно играть против другого игрока (реплай) или против бота.'
}
