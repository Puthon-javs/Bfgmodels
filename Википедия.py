from aiogram import types, Dispatcher
import wikipedia

wikipedia.set_lang("ru")

async def wiki_handler(message: types.Message):
    text = message.text.strip()
    if text.startswith("/википедия") or text.lower().startswith("википедия"):
        query = text.split(" ", 1)
        if len(query) < 2:
            await message.reply("❌ Укажи, что искать. Пример:\n<code>/википедия Python</code>", parse_mode="HTML")
            return

        search_query = query[1]

        try:
            page = wikipedia.page(search_query)
            summary = wikipedia.summary(search_query, sentences=3)
            title = page.title

            response = f"🔍 {title}\n```java\n{summary}\n```"
            await message.reply(response, parse_mode="HTML")

        except wikipedia.exceptions.DisambiguationError as e:
            options = "\n".join(e.options[:5])
            await message.reply(f"⚠️ Запрос слишком общий. Возможные статьи:\n<pre>{options}</pre>", parse_mode="HTML")

        except wikipedia.exceptions.PageError:
            await message.reply("❌ Ничего не найдено по этому запросу.", parse_mode="HTML")

        except Exception as e:
            await message.reply(f"⚠️ Ошибка: <code>{e}</code>", parse_mode="HTML")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(wiki_handler, lambda msg: msg.text.lower().startswith("википедия"))
    dp.register_message_handler(wiki_handler, commands=['википедия'])