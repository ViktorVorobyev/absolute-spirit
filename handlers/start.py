from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart(), F.chat.type == "private")
async def handle_start(message: Message):
    await message.answer("✨ Абсолютный дух пробудился. Пришли своё послание.")

__all__ = ["router"]