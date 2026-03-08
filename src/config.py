import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    TAVILY_API_KEY: str
    GROQ_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    # Database
    DATABASE_URL: str = Field(default="sqlite:///local.db")

    # App Settings
    LOG_LEVEL: str = Field(default="INFO")
    REFRESH_INTERVAL_MINUTES: int = Field(default=60)
    ADMIN_USER_ID: int = Field(default=0)

settings = Settings()
