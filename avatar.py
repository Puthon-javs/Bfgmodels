import os
import sqlite3
import logging
from pathlib import Path
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType

# Импортируем необходимые зависимости (должны быть доступны в вашем проекте)
from assets.antispam import antispam, admin_only
from assets.transform import transform_int as tr
from bot import bot
from commands.help import CONFIG
from user import BFGuser, BFGconst

# --- КОНФИГУРАЦИЯ ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Пути к файлам
BASE_DIR = Path(__file__).parent.parent
AVATARS_DIR = BASE_DIR / 'modules' / 'temp' / 'avatars'
DB_PATH = BASE_DIR / 'modules' / 'temp' / 'avatar.db'

# Создаем директории если их нет
AVATARS_DIR.mkdir(parents=True, exist_ok=True)

# Добавляем команду в помощь
CONFIG['help_osn'] += '\n   🖼 Аватарка - установить/удалить аватар'

# --- СОСТОЯНИЯ FSM ---
class SetAvaState(StatesGroup):
    avatar = State()

# --- БАЗА ДАННЫХ ---
class AvatarDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_tables()
    
    def _create_tables(self):
        """Создание таблиц если они не существуют"""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    action INTEGER DEFAULT 0
                )''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    chat_id INTEGER DEFAULT 0
                )''')
            
            # Инициализация настроек
            if not self.conn.execute('SELECT 1 FROM settings').fetchone():
                self.conn.execute('INSERT INTO settings (id, chat_id) VALUES (1, 0)')
    
    async def get_moderation_chat(self):
        """Получить ID чата для модерации"""
        try:
            return self.conn.execute('SELECT chat_id FROM settings WHERE id = 1').fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка получения чата модерации: {e}")
            return 0
    
    async def set_moderation_chat(self, chat_id):
        """Установить чат для модерации"""
        try:
            with self.conn:
                self.conn.execute('UPDATE settings SET chat_id = ? WHERE id = 1', (chat_id,))
            return True
        except Exception as e:
            logger.error(f"Ошибка установки чата модерации: {e}")
            return False
    
    async def get_avatar_status(self, user_id):
        """Получить статус аватарки (None - нет, 0 - на модерации, 1 - одобрено)"""
        try:
            result = self.conn.execute(
                'SELECT action FROM users WHERE user_id = ?', 
                (user_id,)
            ).fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка получения статуса аватарки: {e}")
            return None
    
    async def add_for_moderation(self, user_id):
        """Добавить аватарку на модерацию"""
        try:
            with self.conn:
                self.conn.execute(
                    'INSERT OR REPLACE INTO users (user_id, action) VALUES (?, 0)',
                    (user_id,)
                )
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления на модерацию: {e}")
            return False
    
    async def update_status(self, user_id, status):
        """Обновить статус аватарки (1 - одобрено, 0 - отклонено)"""
        try:
            with self.conn:
                if status == 1:
                    self.conn.execute(
                        'UPDATE users SET action = 1 WHERE user_id = ?',
                        (user_id,)
                    )
                else:
                    self.conn.execute(
                        'DELETE FROM users WHERE user_id = ?',
                        (user_id,)
                    )
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления статуса: {e}")
            return False
    
    def close(self):
        """Закрыть соединение с БД"""
        self.conn.close()

# Инициализация БД
db = AvatarDatabase()

# --- КЛАВИАТУРЫ ---
def get_avatar_kb(user_id, has_avatar):
    """Клавиатура управления аватаркой"""
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='❌ Удалить' if has_avatar else '🖼 Установить',
            callback_data=f"avatar_toggle|{user_id}"
        )
    )

def get_cancel_kb():
    """Клавиатура отмены"""
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("❌ Отмена", callback_data="avatar_cancel")
    )

def get_moderation_kb(user_id):
    """Клавиатура для модераторов"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✅ Одобрить", callback_data=f"avatar_approve|{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"avatar_reject|{user_id}")
    )

# --- КОМАНДЫ ---
@antispam
async def balance_cmd(message: types.Message, user: BFGuser):
    """Показать баланс с возможной аватаркой"""
    avatar_status = await db.get_avatar_status(user.id)
    
    balance_text = f'''👫 Ник: {user.name}
💰 Деньги: {user.balance.tr()}$
💴 Йены: {user.yen.tr()}¥
🏦 Банк: {user.bank.tr()}$
💽 Биткоины: {user.btc.tr()}🌐

{BFGconst.ads}'''
    
    if avatar_status == 1:
        avatar_path = AVATARS_DIR / f"{user.id}.png"
        try:
            with open(avatar_path, 'rb') as avatar_file:
                await message.answer_photo(
                    photo=avatar_file,
                    caption=balance_text,
                    reply_markup=get_avatar_kb(user.id, True)
                )
        except Exception as e:
            logger.error(f"Ошибка отправки аватарки: {e}")
            await db.update_status(user.id, 0)
            await message.answer(balance_text, disable_web_page_preview=True)
    else:
        await message.answer(
            balance_text,
            disable_web_page_preview=True,
            reply_markup=get_avatar_kb(user.id, False)
        )

@antispam
async def profile_cmd(message: types.Message, user: BFGuser):
    """Показать профиль с аватаркой"""
    avatar_status = await db.get_avatar_status(user.id)
    
    profile_text = f'''👤 Профиль {user.name}:
🪪 ID: {user.id}
💰 Баланс: {user.balance.tr()}$
💴 Йены: {user.yen.tr()}¥
🏦 В банке: {user.bank.tr()}$
💽 Биткоины: {user.btc.tr()}🌐
⚡ Энергия: {user.energy.tr()}
🏅 Рейтинг: {user.rating.tr()}
📅 Регистрация: {user.reg_date}

{BFGconst.ads}'''
    
    if avatar_status == 1:
        avatar_path = AVATARS_DIR / f"{user.id}.png"
        try:
            with open(avatar_path, 'rb') as avatar_file:
                await message.answer_photo(
                    photo=avatar_file,
                    caption=profile_text,
                    reply_markup=get_avatar_kb(user.id, True)
                )
        except Exception as e:
            logger.error(f"Ошибка отправки аватарки: {e}")
            await db.update_status(user.id, 0)
            await message.answer(profile_text, disable_web_page_preview=True)
    else:
        await message.answer(
            profile_text,
            disable_web_page_preview=True,
            reply_markup=get_avatar_kb(user.id, False)
        )

@antispam
async def avatar_cmd(message: types.Message, user: BFGuser):
    """Управление аватаркой"""
    avatar_status = await db.get_avatar_status(user.id)
    
    if avatar_status == 1:
        avatar_path = AVATARS_DIR / f"{user.id}.png"
        try:
            with open(avatar_path, 'rb') as avatar_file:
                await message.answer_photo(
                    photo=avatar_file,
                    caption=f"🖼 {user.name}, ваша аватарка",
                    reply_markup=get_avatar_kb(user.id, True)
                )
        except Exception as e:
            logger.error(f"Ошибка отправки аватарки: {e}")
            await db.update_status(user.id, 0)
            await message.answer("❌ Не удалось загрузить аватарку")
    else:
        status_text = "🖼 У вас нет аватарки" if avatar_status is None else "🔄 Аватарка на проверке"
        await message.answer(
            status_text,
            reply_markup=get_avatar_kb(user.id, False)
        )

# --- ОБРАБОТЧИКИ ---
async def toggle_avatar(call: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки управления аватаркой"""
    user_id = call.from_user.id
    target_id = int(call.data.split('|')[1])
    
    if user_id != target_id:
        return await call.answer("❌ Это не ваша аватарка!", show_alert=True)
    
    avatar_status = await db.get_avatar_status(user_id)
    
    if avatar_status == 1:  # Удаление
        avatar_path = AVATARS_DIR / f"{user_id}.png"
        if avatar_path.exists():
            avatar_path.unlink()
        await db.update_status(user_id, 0)
        await call.message.edit_caption("🗑 Аватарка удалена!")
    else:  # Установка новой
        if avatar_status == 0:
            return await call.answer("🔄 Ваша аватарка уже на проверке!", show_alert=True)
        
        await call.message.edit_text(
            "📤 Отправьте мне изображение для аватарки:",
            reply_markup=get_cancel_kb())
        await SetAvaState.avatar.set()

async def cancel_avatar(call: types.CallbackQuery, state: FSMContext):
    """Отмена установки аватарки"""
    await state.finish()
    await call.message.delete()

async def process_avatar(message: types.Message, state: FSMContext):
    """Обработка полученной аватарки"""
    user_id = message.from_user.id
    mod_chat = await db.get_moderation_chat()
    
    if not mod_chat:
        await message.answer("❌ Система аватарок временно недоступна")
        await state.finish()
        return
    
    try:
        # Сохраняем фото
        avatar_path = AVATARS_DIR / f"{user_id}.png"
        await message.photo[-1].download(destination_file=avatar_path)
        
        # Отправляем на модерацию
        with open(avatar_path, 'rb') as avatar_file:
            await bot.send_photo(
                chat_id=mod_chat,
                photo=avatar_file,
                caption=f"🖼 Новая аватарка от {user_id}",
                reply_markup=get_moderation_kb(user_id))
        
        await db.add_for_moderation(user_id)
        await message.answer("✅ Аватарка отправлена на модерацию!")
    except Exception as e:
        logger.error(f"Ошибка обработки аватарки: {e}")
        await message.answer("❌ Не удалось обработать изображение")
    finally:
        await state.finish()

@admin_only
async def set_mod_chat(message: types.Message):
    """Установка чата для модерации"""
    chat_id = message.chat.id
    if await db.set_moderation_chat(chat_id):
        await message.answer(f"✅ Чат для модерации установлен: {chat_id}")
    else:
        await message.answer("❌ Не удалось установить чат модерации")

async def moderate_avatar(call: types.CallbackQuery):
    """Модерация аватарок"""
    action, user_id = call.data.split('|')
    user_id = int(user_id)
    
    if 'approve' in action:
        await db.update_status(user_id, 1)
        text = f"✅ Аватарка {user_id} одобрена"
    else:
        avatar_path = AVATARS_DIR / f"{user_id}.png"
        if avatar_path.exists():
            avatar_path.unlink()
        await db.update_status(user_id, 0)
        text = f"❌ Аватарка {user_id} отклонена"
    
    await call.message.edit_caption(text)

# --- РЕГИСТРАЦИЯ ---
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(balance_cmd, lambda m: m.text.lower() in ['б', 'баланс', 'balance'])
    dp.register_message_handler(profile_cmd, lambda m: m.text.lower() in ['профиль', 'п', 'profile'])
    dp.register_message_handler(avatar_cmd, lambda m: m.text.lower() in ['ава', 'аватарка', 'avatar'])
    dp.register_callback_query_handler(toggle_avatar, text_startswith='avatar_toggle')
    dp.register_callback_query_handler(cancel_avatar, text='avatar_cancel', state=SetAvaState.avatar)
    dp.register_message_handler(process_avatar, content_types=ContentType.PHOTO, state=SetAvaState.avatar)
    dp.register_message_handler(set_mod_chat, commands=['set_avatar_chat'])
    dp.register_callback_query_handler(moderate_avatar, text_startswith='avatar_')

MODULE_DESCRIPTION = {
    'name': '🖼 Аватарки',
    'description': (
        "Система пользовательских аватарок\n"
        "Команды:\n"
        "• ава - управление аватаркой\n"
        "• баланс - просмотр баланса\n"
        "• профиль - информация о пользователе\n"
        "Для админов:\n"
        "/set_avatar_chat - установить чат модерации"
    )
}

# Закрытие БД при завершении
def shutdown():
    db.close()