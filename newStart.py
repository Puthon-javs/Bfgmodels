from aiogram import types
from aiogram.dispatcher import Dispatcher
import random


async def start(message: types.Message):
    greetings = [
        'Привет! 😊',
        'Здравствуй! 👋',
        'Приветствую тебя! 🤗',
        'Хай! 😎',
        'Доброго времени суток! 🕰️'
    ]
    await message.answer(random.choice(greetings))


async def botyara(message: types.Message):
    random_message = random.choice([
        "Я тут! 😊", 
        "На месте! 👍", 
        "Работаю! 💻",
        "Что случилось? 💜",
        "Готов помочь! 🤖",
        "Слушаю тебя! 👂",
        "Здесь и жду твоих команд! ⏳"
    ])
    await message.reply(random_message)


async def how_are_you(message: types.Message):
    answers = [
        "Отлично! 😃 А у тебя?",
        "Прекрасно, как никогда! 🌟",
        "Нормально, работаю... 💼",
        "Лучше всех! 😎",
        "Бывало и лучше, бывало и хуже 🤷‍♂️",
        "Как у бота - без эмоций, но работает! 🩵"
    ]
    await message.reply(random.choice(answers))


async def whats_your_name(message: types.Message):
    names = [
        "Меня зовут как-то но я хз как! 😊",
        "Я - твой верный бот-помощник! 💙",
        "Имя мне Ботяра, но ты можешь придумать своё 😊",
        "Я просто бот, но ты можешь называть меня как хочешь! 😄",
        "Ботяра к твоим услугам! ✨"
    ]
    await message.reply(random.choice(names))


async def unknown_command(message: types.Message):
    responses = [
        "Не совсем понимаю... 🤔",
        "Можешь повторить? 👂",
        "Я не знаю такой команды 😕",
        "Попробуй что-то другое 🔄",
        "Моя твоя не понимать... 🌐"
    ]
    await message.reply(random.choice(responses))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, lambda message: message.text.lower().startswith('привет'))
    dp.register_message_handler(botyara, lambda message: message.text.lower().startswith('бот'))
    dp.register_message_handler(how_are_you, lambda message: message.text.lower().startswith('как дела'))
    dp.register_message_handler(whats_your_name, lambda message: message.text.lower().startswith('как тебя зовут'))
    dp.register_message_handler(unknown_command, lambda message: message.text.lower().startswith('стат'))
