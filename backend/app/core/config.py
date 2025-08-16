from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    async_database_url: str = "sqlite+aiosqlite:///./onlinesim.db"
    database_echo: bool = False
    
    # FastAPI
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    cors_origins_str: str = ""  # Строка из .env
    
    # SMS Service
    sms_provider: str = "smsactivate"
    sms_api_key: str = "1994406e9987d71A986488df8878b26A"
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
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_port: int = 3000
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Получить список разрешенных CORS origins"""
        # Читаем напрямую из переменной окружения
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
        
        # Если в self.cors_origins_str что-то есть
        if self.cors_origins_str:
            return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
        
        # Fallback для разработки
        return ["http://localhost:5173", "http://localhost:3000", "https://app2.hezh-digital.ru"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Маппинг для переменной CORS_ORIGINS
        fields = {
            'cors_origins_str': {
                'env': 'CORS_ORIGINS'
            }
        }

settings = Settings()