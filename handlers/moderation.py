import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message

from core.bot_instance import bot, gpt_client
from core.constants import RESPONSES, EMPTY_RESPONSES
from core.config import TARGET_CHAT_ID

router = Router()

from core.persona import BOT_CHARACTER  # Характер бота

# Анонимное сообщение → в группу
@router.message(F.chat.type == "private")
async def handle_private_message(message: Message):
    text = message.text or ""
    if not text.strip():
        await message.answer(random.choice(EMPTY_RESPONSES))
        return

    await message.chat.do("typing")

    # 🧠 Проверка текста через GPT
    try:
        moderation_prompt = (f"""
            Ты — модератор чата
            {BOT_CHARACTER}
            Проанализируй сообщение и оцени, можно ли публиковать его в анонимной группе.
            Запрещены: прямые оскорбления, разжигание ненависти (национальной, расовой, половой), агрессия, непристойность, травля, неприемлемый сексуальный или садистский контекст, чрезмерное использование непонятных символов, бессмысленных рисунков из символов (ASCII-арт), однотипных повторяющихся строк, шума или спама.
            Допустимы: ирония, сарказм, критика, даже если они могут быть провокационными, но не нарушают прямые запреты.
            Допустимы исключения слов и их вариаций: гойда.
            Если сообщение приемлемо — ответь строго OK. Если нет — объясни, почему именно оно нарушает правила, просто укажи причину, например: ASCII-спам, нецензурная лексика, разжигание ненависти.
            """
        )

        messages = [
            {"role": "system", "content": moderation_prompt},
            {"role": "user", "content": text}
        ]

        moderation_response = await asyncio.to_thread(
            gpt_client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.0,
            max_tokens=100,
        )

        result = moderation_response.choices[0].message.content.strip()

        if result.upper().startswith("OK"):
            await bot.send_message(chat_id=TARGET_CHAT_ID, text=text)
            await message.answer(random.choice(RESPONSES))
        else:
            await message.answer(f"⚠️ Абсолютный дух отклонил послание:\n{result}")

    except Exception as e:
        print(f"❌ Ошибка проверки сообщения: {e}")
        await message.answer("⚠️ Абсолютный дух не смог проверить послание. Попробуй позже.")

__all__ = ["router"]