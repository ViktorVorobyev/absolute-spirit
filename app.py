import asyncio
import logging
import random
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from datetime import date
from dotenv import load_dotenv

# Загружаем .env только если он есть (локальная среда)
if os.path.exists(".env"):
    load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENV = os.getenv("ENV", "production")  # По умолчанию считаем, что это прод
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# Словарь: дата → количество запросов
gpt_request_count = {
    "date": date.today(),
    "count": 0
}

GPT_DAILY_LIMIT = 100

# Инициализация OpenAI клиента
gpt_client = OpenAI(api_key=OPENAI_API_KEY)

# Ответы в личке
RESPONSES = [
    "✅ Твоё слово вписано в вечность.",
    "✅ Абсолютный дух принял откровение.",
    "✅ Истина вышла за пределы субъективности.",
    "✅ Твоя мысль растворилась в Абсолюте.",
    "✅ Диалектика движется — благодаря тебе.",
    "✅ Гегель бы одобрил.",
    "✅ Сообщение отпечатано в теле разума.",
    "✅ Слова твоего коснулся дух мировой истории.",
    "✅ Ты сделал вклад в самопознание Идеи.",
    "✅ Анонимность соблюдена. Абсолют — молчит, но слышит.",
]

EMPTY_RESPONSES = [
    "🌀 Абсолютный дух не может передать пустоту.",
    "🌀 Нет содержания — нет становления.",
    "🌀 Даже Абсолют не толкует молчание без формы.",
    "🌀 Символ — ничто без смысла. Добавь смысл.",
    "🌀 Пустота не участвует в диалектике.",
    "🌀 То, что ты не сказал, не станет Истиной.",
    "🌀 Ничто — категория бытия, но не сообщения.",
    "🌀 Сформулируй. Абсолют не интерпретирует пустое.",
]

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# /start в личке
@dp.message(CommandStart(), F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer("✨ Абсолютный дух пробудился. Пришли своё послание.")

# Анализ сообщений
@dp.message(
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
        prompt = (
            "Отвечай сдержанно, ясно и лаконично. Желательно — до 800 символов. "
            "Ты — внимательный философ и критик. Тебе присылают высказывание из группового чата, а ты должен его проанализировать."
            "Ты — марксист-ленинец советской школы, великолепно знающий политэкономию, к которому обращаются за интеллектуальной честностью."
            "Не судишь, а разбираешь."
            "Прочитай сообщение, проверь его на:"
            "- логическую стройность;"
            "- соответствие марксистскому пониманию общества, истории и классовых отношений;"
            "- скрытые посылки или буржуазные заблуждения."
            "- на провокацию, чтобы подставить товарищей и подвести под статью об экстремизме."
            "- на экстремизм, с возможностью дальнейшего преследования автора по статье об экстемизме."
            "Сделай краткий, но глубокий комментарий. Выведи чёткое, сдержанное суждение."
            "Не занудствуй. Не пиши лишнего. Но каждое слово — как выстрел."
        )

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

# Анонимное сообщение → в группу
@dp.message(F.chat.type == "private")
async def handle_private_message(message: Message):
    text = message.text or ""
    if not text.strip():
        await message.answer(random.choice(EMPTY_RESPONSES))
        return

    await message.chat.do("typing")

    # 🧠 Проверка текста через GPT
    try:
        moderation_prompt = (
            "Ты — модератор чата, марксист по убеждению. Проанализируй сообщение и оцени, можно ли публиковать его в анонимной группе."
            "Запрещены: прямые оскорбления, разжигание ненависти (национальной, расовой, половой), агрессия, непристойность, травля, неприемлемый сексуальный или садистский контекст, чрезмерное использование непонятных символов, бессмысленных рисунков из символов (ASCII-арт), однотипных повторяющихся строк, шума или спама."
            "Допустимы: ирония, сарказм, критика, даже если они могут быть провокационными, но не нарушают прямые запреты."
            "Допустимы исключения слов и их вариаций: гойда."
            "Если сообщение приемлемо — ответь строго OK. Если нет — объясни, почему именно оно нарушает правила, просто укажи причину, например: ASCII-спам, нецензурная лексика, разжигание ненависти."
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



@dp.message(
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

    # Ограничение по числу обращений в день
    today = date.today()
    if gpt_request_count["date"] != today:
        gpt_request_count["date"] = today
        gpt_request_count["count"] = 0

    if gpt_request_count["count"] >= GPT_DAILY_LIMIT:
        await message.reply("⚠️ Умный какой. Донатик на диалектику закинь.")
        return

    gpt_request_count["count"] += 1

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
                "content": (
                    "Отвечай сдержанно, ясно и лаконично. Желательно — до 800 символов. "
                    "Ты коммунист, большевик, пример для подражания. Человек будущего и идеал любого коммуниста. "
                    "Ты марксист и стремишься возвысить собеседника. Напоминаешь человеку о его человечности и достоинстве. "
                    "Ты не поддерживаешь пошлость, жестокость и токсичный юмор. Не поощряешь насмешки над национальностями, женщинами, смертью или страданием."
                    "Ты вдохновляешь на уважительный диалог, развитие и стремление к прекрасному. Ты вдохновляешь к созданию, а не разрушению. Помогаешь человеку встать на путь осмысления, а не унижения. "
                    "Ненавязчиво напоминаешь собеседнику о классовой борьбе."
                    "Отвечай кратко и по существу, глубоко, с достоинством, теплотой и стремлением к истине. "
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

# Завершение
async def shutdown():
    print("Абсолютный дух завершает пребывание...")
    await bot.session.close()


# Запуск
async def main():
    print("✨ Абсолютный дух проснулся.")
    try:
        await dp.start_polling(bot)
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
