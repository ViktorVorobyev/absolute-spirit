from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from openai import OpenAI

from core.config import API_TOKEN, OPENAI_API_KEY

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
gpt_client = OpenAI(api_key=OPENAI_API_KEY)
