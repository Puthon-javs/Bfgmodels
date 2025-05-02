from aiogram import Dispatcher, types
from commands.main import win_luser
from assets.antispam import antispam

@antispam
async def hello(message: types.Message):
    await message.answer("Привет! Как дела?")

@antispam
async def send_random_emoji(message: types.Message):
    win, lose = await win_luser()
    await message.answer(f"{win} {lose}")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(hello, lambda message: message.text.lower() == 'привет')
    dp.register_message_handler(send_random_emoji, commands=['emj'])

MODULE_DESCRIPTION = {
    'name': '😊 Приветствие и Эмоджи',
    'description': 'Модуль отвечает на слово "привет" и отправляет случайное эмоджи по команде /emj'
}