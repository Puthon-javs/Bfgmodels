from aiogram import Dispatcher, types
from commands.main import win_luser  # Импортируем случайные эмоджи
from assets.antispam import antispam  # Импортируем антиспам

# Функция, которая отвечает на слово "привет"
@antispam
async def hello(message: types.Message):
    await message.answer("Привет! Как дела?")

# Функция для отправки случайного эмоджи
@antispam
async def send_random_emoji(message: types.Message):
    win, lose = await win_luser()  # Получаем случайные эмоджи
    await message.answer(win, lose)  # Отправляем случайные эмоджи

# Функция для регистрации хэндлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(hello, lambda message: message.text.lower() == 'привет')
    dp.register_message_handler(send_random_emoji, commands=['emj'])

# Описание модуля
MODULE_DESCRIPTION = {
    'name': '😊 Приветствие и Эмоджи',
    'description': 'Модуль отвечает на слово "привет" и отправляет случайное эмоджи по команде /emj'
}