from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database - асинхронные URL
    #database_url: str = "sqlite:///./onlinesim.db"
    async_database_url: str = "sqlite+aiosqlite:///./onlinesim.db"
    database_echo: bool = False
    
    # FastAPI
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # SMS Service
    sms_provider: str = "dummy"
    sms_api_key: str = ""
    sms_api_url: str = "https://api.sms-service.com"
    sms_webhook_secret: str = "webhook-secret-key"
    
    # Order Settings
    order_timeout_minutes: int = 15
    api_timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Telegram Bot
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    webapp_url: str = "http://localhost:3000"
    
    # CORS
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Получить список разрешенных CORS origins"""
        origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        return [origin.strip() for origin in origins.split(",") if origin.strip()]
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_port: int = 3000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()