from aiogram import types, Dispatcher

HELP_TEXT = """
🆘 <b>Справка по модулям и командам:</b>

<b>📦 МОДУЛЬ: Побег</b>
🔓 <code>побег</code> — Начать побег из тюрьмы. Назначается статья, запускается сюжет побега.  
📜 <code>моя статья</code> — Показать свою текущую статью по УК РФ.  
📊 <code>мой побег</code> — Статистика: победы, поражения, медали.  
🏆 <code>топ побегов</code> — Топ игроков по успешным побегам.  
❓ <code>побег помощь</code> — Справка по побегу.

<b>💬 Основные команды:</b>
<code>привет</code>, <code>ботяра</code>, <code>я кто</code>, <code>как дела</code> — простые команды.  
<code>шутка</code> — IT-шутка.  
<code>ск</code> (в ответ) — обзывалка.  
<code>моя статья</code> — статья по УК РФ.  
<code>пинг</code>, <code>.ping</code>, <code>!ping</code> — проверить пинг.  
<code>покажи</code> — пинг + статистика.  
<code>статистика</code> — только для админа.

<b>🔐 Админ-команды:</b>
<code>статистика</code> — активность, команды, приколы.  
<code>админ</code>, <code>позвать админа</code> — вызов админа  
<code>позвать Еву</code> — вызывает Еву  
<code>обратиться в поддержку</code> — отправка обращения в ЛС владельца  

<b>🏗️ Модуль: Бункер</b>
📍 <code>/бункер</code>, <code>/улучшить бункер</code>, <code>/строить склад</code>, <code>/улучшить склад</code>, <code>/склад</code>  
📦 <code>/добывать металл</code> — добыча ресурсов  
💱 <code>/торговать @user металл 100 50</code> — торговля  
⚔️ <code>/мутант</code> — бой с мутантом  
🧟‍♂️ <code>/осада</code> — зомби-атака  
🗺️ <code>/карта</code> — карта угроз (изображение)  
🆘 <code>/репорт</code> — отправить репорт  
🔍 <code>/википедия</code> — поиск по Википедии
"""

async def cmd_pomogi(message: types.Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_pomogi, lambda msg: msg.text.lower() == 'помоги')