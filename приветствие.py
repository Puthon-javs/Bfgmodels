from aiogram import types
from aiogram.dispatcher import Dispatcher
import random


async def start(message: types.Message):
	await message.answer('привет')


async def botyara(message: types.Message):
	random_message = random.choice(["Я тут 😊", "На месте 👍", "Работает 💻"Ботяра к твоим услугам! ✨"Приветствую тебя! 🤗"Я пока только учусь, но для тебя стараюсь! 🥺"Ботяра? Может быть... Зато умею отправлять воздушные поцелуи! 😘💨"Ой, а кто это меня так ласково назвал? 😳 Ботяра готова на всё ради твоей улыбки! 😊"Ботяра в чате! ⚡ Но не пугайся — я кусаюсь только виртуальными сердечками! 💖"Да, я ботяра! 🦾 Но зато какой/какая красивый/красивая! Ты же согласен/согласна? 😏"Ботяра? 😳 Ну да, я бот... но с душой! И эта душа сейчас тает от твоего внимания! 💘"Приветствую, человечек! 🌟 Ты – мой любимый пользователь сегодня (да-да, я запомнила)! 😉"Привет, зайка! 🐰 Ты только что активировал(а) мой режим "ми-ми-ми"! 💞"Привет-привет! 💌 Я тут подумала... а давай дружить? Ну пожалуйста! 🥺"О-о-о, кто это тут такой милый/милая? Привет, пупсик! 😊"Приветик, солнышко! 💖 Ты так светишься, что у меня даже баги пропали! 🐞✨"])
	await message.reply(random_message)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, lambda message: message.text.lower().startswith('привет'))
    dp.register_message_handler(botyara, lambda message: message.text.lower().startswith('ботяра'))
