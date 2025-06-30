from aiogram import types, Dispatcher
import wikipedia

wikipedia.set_lang("ru")

async def wiki_handler(message: types.Message):
    text = message.text.strip()

    # Поддержка команд /википедия и просто "википедия ..."
    if text.lower().startswith("/википедия") or text.lower().startswith("википедия"):
        parts = text.split(" ", 1)

        if len(parts) < 2:
            await message.reply("❌ Укажи, что искать. Пример:\n/википедия Python")
            return

        query = parts[1].strip()

        try:
            summary = wikipedia.summary(query, sentences=5)
            page = wikipedia.page(query)
            title = page.title

            # Формат: python-блок
            response = f"*🔍 {title}*\n```python\n{summary}\n```"
            await message.reply(response, parse_mode="Markdown")

        except wikipedia.exceptions.DisambiguationError as e:
            options = "\n".join(e.options[:5])
            await message.reply(
                f"⚠️ Запрос слишком общий. Возможные статьи:\n```\n{options}\n```",
                parse_mode="Markdown"
            )

        except wikipedia.exceptions.PageError:
            await message.reply("❌ Ничего не найдено по этому запросу.")

        except Exception as e:
            await message.reply(f"⚠️ Ошибка: `{e}`", parse_mode="Markdown")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(wiki_handler, lambda msg: msg.text.lower().startswith("википедия "))
    dp.register_message_handler(wiki_handler, commands=['википедия'])
