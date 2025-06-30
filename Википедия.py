from aiogram import types, Dispatcher
import wikipedia
import re

# Устанавливаем язык
wikipedia.set_lang("ru")

def escape_md(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2
    """
    return re.sub(r'([_*()~`>#+=|{}.!\\-])', r'\\\1', text)

async def wikipedia_handler(message: types.Message):
    text = message.text.strip()

    if text.startswith("/википедия") or text.lower().startswith("википедия "):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            await message.reply("❗ Укажи, что искать. Пример: `/википедия Python`", parse_mode="MarkdownV2")
            return

        query = parts[1]

        try:
            # Поиск статьи
            page = wikipedia.page(query)
            summary = wikipedia.summary(query, sentences=5)

            title = escape_md(page.title)
            content = escape_md(summary)

            # Формируем ответ
            response = f"🔍 *{title}*\n```java\n{content}\n```"
            await message.reply(response, parse_mode="MarkdownV2")

        except wikipedia.exceptions.DisambiguationError as e:
            options = "\n".join([escape_md(opt) for opt in e.options[:5]])
            await message.reply(f"⚠️ Запрос слишком общий, уточни:\n```{options}```", parse_mode="MarkdownV2")

        except wikipedia.exceptions.PageError:
            await message.reply("❌ Статья не найдена.", parse_mode="MarkdownV2")

        except Exception as e:
            error = escape_md(str(e))
            await message.reply(f"⚠️ Ошибка:\n```{error}```", parse_mode="MarkdownV2")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(wikipedia_handler, lambda msg: msg.text.lower().startswith("википедия"))
    dp.register_message_handler(wikipedia_handler, commands=["википедия"])
