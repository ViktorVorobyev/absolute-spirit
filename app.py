import asyncio
import logging

from aiogram import Dispatcher

from core.bot_instance import bot
from db.database import init_db
from handlers import start, analysis, moderation, gpt_reply
from middlewares.save_message import SaveMessageMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация диспетчера и подключение роутеров
dp = Dispatcher()
dp.include_router(start.router)
dp.message.middleware(SaveMessageMiddleware())
dp.include_router(analysis.router)
dp.include_router(moderation.router)
dp.include_router(gpt_reply.router)

# Завершение
async def shutdown():
    print("Абсолютный дух завершает пребывание...")
    await bot.session.close()

# Основная функция запуска
async def main():
    init_db()
    print("✨ Абсолютный дух проснулся.")
    try:
        await dp.start_polling(bot)
    finally:
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())
