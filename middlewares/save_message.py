# middlewares/save_message.py

from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from db.database import save_message
import logging

logging.basicConfig(level=logging.INFO)

class SaveMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.chat.type in {"group", "supergroup"}:
            text = event.text or event.caption
            if not text:
                return await handler(event, data)

            reply_to_text = None
            if event.reply_to_message:
                reply_to_text = event.reply_to_message.text or event.reply_to_message.caption

            logging.info(f"💬 Получено сообщение: {text}")
            save_message(
                user_id=event.from_user.id,
                chat_id=event.chat.id,
                text=text,
                reply_to_text=reply_to_text
            )

        return await handler(event, data)
