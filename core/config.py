import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
ENV = os.getenv("ENV", "production")
