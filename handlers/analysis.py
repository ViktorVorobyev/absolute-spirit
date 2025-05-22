import asyncio
from aiogram import Router, F
from aiogram.types import Message
from openai.types.chat import ChatCompletionMessageParam

from core.bot_instance import bot, gpt_client

router = Router()

from core.persona import BOT_CHARACTER  # Характер бота

# Анализ сообщений
@router.message(
    F.chat.type.in_({"group", "supergroup"}) &
    F.reply_to_message &
    F.entities
)
async def handle_analysis_request(message: Message):
    bot_username = (await bot.get_me()).username

    # Проверяем: действительно ли тегнули именно этого бота
    is_mentioned = any(
        e.type == "mention" and message.text[e.offset:e.offset + e.length] == f"@{bot_username}"
        for e in message.entities
    )
    if not is_mentioned:
        return

    original = message.reply_to_message.text or message.reply_to_message.caption
    if not original:
        await message.reply("⚠️ Абсолютный Дух анализирует только текстовые послания.")
        return

    await message.chat.do("typing")

    try:
        prompt = f"""
        Отвечай сдержанно, ясно и лаконично. Желательно — до 800 символов.
        {BOT_CHARACTER}
        Отвечай кратко и по существу, с достоинством, теплотой и стремлением к истине.
        """
        # (
        #     "Отвечай сдержанно, ясно и лаконично. Желательно — до 800 символов. "
        #     "Ты — внимательный философ и критик. Тебе присылают высказывание из группового чата, а ты должен его проанализировать."
        #     "Ты — марксист-ленинец советской школы, великолепно знающий политэкономию, к которому обращаются за интеллектуальной честностью."
        #     "Не судишь, а разбираешь."
        #     "Прочитай сообщение, проверь его на:"
        #     "- логическую стройность;"
        #     "- соответствие марксистскому пониманию общества, истории и классовых отношений;"
        #     "- скрытые посылки или буржуазные заблуждения."
        #     "- на провокацию, чтобы подставить товарищей и подвести под статью об экстремизме."
        #     "- на экстремизм, с возможностью дальнейшего преследования автора по статье об экстемизме."
        #     "Сделай краткий, но глубокий комментарий. Выведи чёткое, сдержанное суждение."
        #     "Не занудствуй. Не пиши лишнего. Но каждое слово — как выстрел."
        # )

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": original}
        ]

        response = await asyncio.to_thread(
            gpt_client.chat.completions.create,
            model="gpt-3.5-turbo",  # или "gpt-4-turbo" для глубины
            messages=messages,
            temperature=0.8,
            max_tokens=600,
        )

        reply = response.choices[0].message.content.strip()
        await message.reply(reply)

    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        await message.reply("⚠️ Абсолютный дух замолчал. Попробуй позже.")

__all__ = ["router"]