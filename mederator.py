from aiogram import Bot, types
from aiogram.utils.exceptions import BadRequest
from datetime import datetime, timedelta
import asyncio

class TelegramModerator:
    """
    Модуль модерации для Telegram-бота.
    Поддерживает команды:
    - бан [ID] [время] [причина]
    - разбан [ID]
    - варн [ID] [время] [причина]
    - снятьварн [ID]
    - мут [ID] [время] [причина]
    - размут [ID]
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def _parse_time(self, time_str: str) -> timedelta:
        """Парсит строку времени (например: '1 час', '3 дня')"""
        time_units = {
            'сек': 'seconds',
            'мин': 'minutes',
            'час': 'hours',
            'день': 'days',
            'недел': 'weeks'
        }

        parts = time_str.split()
        if len(parts) != 2:
            return timedelta(days=3)  # Значение по умолчанию

        num, unit = parts
        num = int(num) if num.isdigit() else 3  # Дефолтное значение если не число

        for short, full in time_units.items():
            if unit.startswith(short):
                return timedelta(**{full: num})

        return timedelta(days=3)  # Если формат не распознан

    async def ban_user(
        self,
        chat_id: int,
        user_id: int,
        duration: str = "3 дня",
        reason: str = "Не указана"
    ) -> str:
        """Бан пользователя с возможностью указать время"""
        try:
            delta = await self._parse_time(duration)
            until_date = datetime.now() + delta

            await self.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=until_date
            )

            # Авторазбан через время
            if delta:
                async def auto_unban():
                    await asyncio.sleep(delta.total_seconds())
                    await self.bot.unban_chat_member(chat_id, user_id)
                asyncio.create_task(auto_unban())

            return (f"🔨 Пользователь {user_id} забанен\n"
                    f"⏳ Срок: {duration}\n"
                    f"📝 Причина: {reason}")

        except BadRequest as e:
            return f"❌ Ошибка бана: {e}"

    async def unban_user(self, chat_id: int, user_id: int) -> str:
        """Разбан пользователя"""
        try:
            await self.bot.unban_chat_member(chat_id, user_id)
            return f"✅ Пользователь {user_id} разбанен"
        except BadRequest as e:
            return f"❌ Ошибка разбана: {e}"

    async def warn_user(self, user_id: int, duration: str = "3 дня", reason: str = "Не указана") -> str:
        """Выдать предупреждение"""
        delta = await self._parse_time(duration)
        return (f"⚠ Пользователь {user_id} получил предупреждение\n"
                f"⏳ Срок: {duration}\n"
                f"📝 Причина: {reason}")

    async def mute_user(
        self,
        chat_id: int,
        user_id: int,
        duration: str = "10 минут",
        reason: str = "Не указана"
    ) -> str:
        """Мут пользователя (запрет отправки сообщений)"""
        try:
            delta = await self._parse_time(duration)
            until_date = datetime.now() + delta

            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                ),
                until_date=until_date
            )

            return (f"🔇 Пользователь {user_id} в муте\n"
                    f"⏳ Срок: {duration}\n"
                    f"📝 Причина: {reason}")

        except BadRequest as e:
            return f"❌ Ошибка мута: {e}"

    async def unmute_user(self, chat_id: int, user_id: int) -> str:
        """Снять мут"""
        try:
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=types.ChatPermissions.all()
            )
            return f"✅ Пользователь {user_id} размучен"
        except BadRequest as e:
            return f"❌ Ошибка снятия мута: {e}"
