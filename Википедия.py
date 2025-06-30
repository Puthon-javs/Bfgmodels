
from aiogram import types, Dispatcher
import openai
from config import API_KEY

openai.api_key = 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

async def handle_wikipedia(message: types.Message):
    if not message.text.lower().startswith("википедия "):
        return

    query = message.text.split(" ", 1)[1].strip()
    if not query:
        await message.reply("❌ Пожалуйста, укажи запрос после слова 'википедия'")
        return

    prompt = f"Представь, что ты Википедия. Ответь кратко и информативно, как энциклопедия, на запрос: {query}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=700,
        )
        result = response.choices[0].message["content"].strip()

        # Отправка с оформлением как код-блок
        await message.reply(f"```java\n{result}\n```", parse_mode="Markdown")

    except Exception as e:
        await message.reply(f"⚠️ Ошибка запроса: {e}")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_wikipedia, lambda msg: msg.text.lower().startswith("википедия "))
