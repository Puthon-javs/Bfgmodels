"""
Telegram Moderation Module
Version: 1.1
Commands: бан, мут, варн, разбан, размут, снятьварн
GitHub: https://raw.githubusercontent.com/[ВАШ_ЛОГИН]/[РЕПОЗИТОРИЙ]/main/moderation.py
"""

from aiogram import Bot, types
from aiogram.utils.exceptions import BadRequest
from datetime import datetime, timedelta
import asyncio

class TelegramModerator:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.temp_data = {
            'bans': {},
            'mutes': {},
            'warns': {}
        }

    async def parse_time(self, text: str) -> timedelta:
        """Парсит время в формате '1 час', '3 дня' и т.д."""
        units = {
            'мин': 'minutes',
            'час': 'hours',
            'день': 'days',
            'дня': 'days',
            'недел': 'weeks'
        }
        
        parts = text.split()
        if len(parts) != 2:
            return timedelta(minutes=10)  # Дефолтное значение для мута
            
        num, unit = parts
        num = int(num) if num.isdigit() else 1
        
        for key in units:
            if unit.startswith(key):
                return timedelta(**{units[key]: num})
                
        return timedelta(days=1)  # Если формат не распознан

    async def ban_user(self, chat_id: int, user_id: int, duration: str = "1 день", reason: str = "Не указана"):
        """Бан пользователя"""
        try:
            delta = await self.parse_time(duration)
            until_date = datetime.now() + delta
            
            await self.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=until_date
            )
            
            # Авторазбан
            if delta:
                async def auto_unban():
                    await asyncio.sleep(delta.total_seconds())
                    await self.unban_user(chat_id, user_id)
                asyncio.create_task(auto_unban())
            
            return f"🔨 Пользователь {user_id} забанен на {duration}\nПричина: {reason}"
        except BadRequest as e:
            return f"❌ Ошибка: {e}"

    async def unban_user(self, chat_id: int, user_id: int):
        """Разбан пользователя"""
        try:
            await self.bot.unban_chat_member(chat_id, user_id)
            return f"✅ Пользователь {user_id} разбанен"
        except BadRequest as e:
            return f"❌ Ошибка: {e}"

    async def mute_user(self, chat_id: int, user_id: int, duration: str = "10 минут", reason: str = "Не указана"):
        """Мут пользователя"""
        try:
            delta = await self.parse_time(duration)
            until_date = datetime.now() + delta
            
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False
                ),
                until_date=until_date
            )
            
            # Авторазмут
            if delta:
                async def auto_unmute():
                    await asyncio.sleep(delta.total_seconds())
                    await self.unmute_user(chat_id, user_id)
                asyncio.create_task(auto_unmute())
            
            return f"🔇 Пользователь {user_id} в муте на {duration}\nПричина: {reason}"
        except BadRequest as e:
            return f"❌ Ошибка: {e}"

    async def unmute_user(self, chat_id: int, user_id: int):
        """Снять мут"""
        try:
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=types.ChatPermissions.all()
            )
            return f"✅ Пользователь {user_id} размучен"
        except BadRequest as e:
            return f"❌ Ошибка: {e}"

    async def warn_user(self, user_id: int, duration: str = "1 день", reason: str = "Не указана"):
        """Выдать предупреждение"""
        delta = await self.parse_time(duration)
        return f"⚠ Пользователь {user_id} получил предупреждение на {duration}\nПричина: {reason}"

    async def unwarn_user(self, user_id: int):
        """Снять предупреждение"""
        return f"✅ С пользователя {user_id} снято предупреждение"
