from aiogram import Dispatcher, types
import logging
from typing import Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from commands.main import win_luser
    from assets.antispam import antispam
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    raise

@antispam
async def hello(message: types.Message):
    """Обработчик приветствия"""
    try:
        await message.answer("Привет! Как дела?")
    except Exception as e:
        logger.error(f"Ошибка в hello: {e}")

@antispam
async def send_random_emoji(message: types.Message):
    """Отправка случайных эмодзи"""
    try:
        result: Tuple[str, str] = await win_luser()
        if not isinstance(result, tuple) or len(result) != 2:
            raise ValueError("Функция win_luser должна возвращать кортеж из двух строк")
            
        win, lose = result
        await message.answer(f"{win} {lose}")
    except Exception as e:
        logger.error(f"Ошибка в send_random_emoji: {e}")
        await message.answer("⚠️ Не удалось получить эмодзи")

def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    try:
        dp.register_message_handler(hello, lambda message: message.text and message.text.lower() == 'привет')
        dp.register_message_handler(send_random_emoji, commands=['emj'])
    except Exception as e:
        logger.error(f"Ошибка регистрации обработчиков: {e}")
        raise

MODULE_DESCRIPTION = {
    'name': '😊 Приветствие и Эмоджи',
    'description': 'Модуль отвечает на слово "привет" и отправляет случайное эмоджи по команде /emj'
}
