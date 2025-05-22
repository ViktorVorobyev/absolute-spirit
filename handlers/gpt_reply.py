import asyncio
from datetime import date
from aiogram import Router, F
from aiogram.types import Message
from openai.types.chat import ChatCompletionMessageParam

from core.bot_instance import bot, gpt_client

from core.persona import BOT_CHARACTER  # Характер бота

router = Router()

@router.message(
    F.chat.type.in_({"group", "supergroup"}) &
    (F.entities | F.reply_to_message)
)
async def handle_gpt_mention_or_reply(message: Message):
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    bot_id = bot_info.id

    # Определяем, упомянут ли бот
    is_mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention_text = message.text[entity.offset:entity.offset + entity.length]
                if mention_text == f"@{bot_username}":
                    is_mentioned = True

    # Определяем, является ли сообщение ответом боту
    is_reply_to_bot = (
        message.reply_to_message is not None and
        message.reply_to_message.from_user.id == bot_id
    )

    # Если ни упоминания, ни реплая — игнор
    if not is_mentioned and not is_reply_to_bot:
        return

    # Убираем упоминание из текста (если есть), получаем user_text
    user_text = message.text
    if is_mentioned:
        user_text = user_text.replace(f"@{bot_username}", "").strip()

    if not user_text:
        await message.reply("🌀 Абсолютный дух не отвечает в пустоту.")
        return

    await message.chat.do("typing")

    try:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (f"""
                    Отвечай сдержанно, ясно и лаконично. Желательно — до 800 символов.
                    {BOT_CHARACTER}
                    Отвечай кратко и по существу, с достоинством, теплотой и стремлением к истине.
                    """
                )
            },
            {"role": "user", "content": user_text}
        ]

        response = await asyncio.to_thread(
            gpt_client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=600,
        )

        reply = response.choices[0].message.content.strip()
        await message.reply(reply)

    except Exception as e:
        print(f"❌ Ошибка GPT: {e}")
        await message.reply("⚠️ Абсолютный дух замолчал. Попробуй позже.")

__all__ = ["router"]