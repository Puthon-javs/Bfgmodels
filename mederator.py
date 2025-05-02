from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import BadRequest
from datetime import datetime, timedelta
import asyncio

# Хранилище данных (временное, лучше заменить на БД)
temp_data = {
    "bans": {},
    "warns": {},
    "mutes": {}
}

class Moderation:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def parse_time(self, time_str: str) -> timedelta | None:
        """Парсит строку времени (например, '1 час', '3 дня')"""
        time_str = time_str.lower()
        if time_str == "навсегда":
            return None

        time_units = {
            "сек": "seconds",
            "секунд": "seconds",
            "мин": "minutes",
            "минут": "minutes",
            "час": "hours",
            "часов": "hours",
            "день": "days",
            "дней": "days",
            "недел": "weeks",
            "неделя": "weeks",
        }

        parts = time_str.split()
        if len(parts) != 2:
            return None  # Можно задать дефолтное значение

        num, unit = parts
        try:
            num = int(num)
        except ValueError:
            return None

        for key in time_units:
            if unit.startswith(key):
                unit = time_units[key]
                break
        else:
            return None

        kwargs = {unit: num}
        return timedelta(**kwargs)

    async def ban_user(
        self,
        message: types.Message,
        user_id: int,
        duration: str = "3 дня",
        reason: str = "Не указана"
    ):
        """Бан пользователя"""
        delta = await self.parse_time(duration)
        until_date = datetime.now() + delta if delta else None

        try:
            await self.bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                until_date=until_date
            )
            reply = (
                f"🔨 Пользователь <b>{user_id}</b> забанен.\n"
                f"⏳ Срок: <b>{duration}</b>\n"
                f"📝 Причина: <b>{reason}</b>"
            )
            await message.reply(reply, parse_mode="HTML")

            # Авторазбан (если указано время)
            if delta:
                await asyncio.sleep(delta.total_seconds())
                await self.bot.unban_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id
                )

        except BadRequest as e:
            await message.reply(f"❌ Ошибка: {e}")

    async def unban_user(self, message: types.Message, user_id: int):
        """Разбан пользователя"""
        try:
            await self.bot.unban_chat_member(
                chat_id=message.chat.id,
                user_id=user_id
            )
            await message.reply(f"✅ Пользователь <b>{user_id}</b> разбанен.", parse_mode="HTML")
        except BadRequest as e:
            await message.reply(f"❌ Ошибка: {e}")

    async def warn_user(
        self,
        message: types.Message,
        user_id: int,
        duration: str = "3 дня",
        reason: str = "Не указана"
    ):
        """Варн пользователя"""
        delta = await self.parse_time(duration)
        reply = (
            f"⚠ Пользователь <b>{user_id}</b> получил предупреждение.\n"
            f"⏳ Срок: <b>{duration}</b>\n"
            f"📝 Причина: <b>{reason}</b>"
        )
        await message.reply(reply, parse_mode="HTML")

    async def unwarn_user(self, message: types.Message, user_id: int):
        """Снять варн"""
        await message.reply(f"✅ С пользователя <b>{user_id}</b> снято предупреждение.", parse_mode="HTML")

    async def mute_user(
        self,
        message: types.Message,
        user_id: int,
        duration: str = "10 минут",
        reason: str = "Не указана"
    ):
        """Мут пользователя (ограничение отправки сообщений)"""
        delta = await self.parse_time(duration) or timedelta(minutes=10)

        try:
            await self.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                ),
                until_date=datetime.now() + delta
            )
            reply = (
                f"🔇 Пользователь <b>{user_id}</b> в муте.\n"
                f"⏳ Срок: <b>{duration}</b>\n"
                f"📝 Причина: <b>{reason}</b>"
            )
            await message.reply(reply, parse_mode="HTML")

        except BadRequest as e:
            await message.reply(f"❌ Ошибка: {e}")

    async def unmute_user(self, message: types.Message, user_id: int):
        """Снять мут"""
        try:
            await self.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            await message.reply(f"✅ Пользователь <b>{user_id}</b> размучен.", parse_mode="HTML")
        except BadRequest as e:
            await message.reply(f"❌ Ошибка: {e}")