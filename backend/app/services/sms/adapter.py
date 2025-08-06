from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SMSOrderResult:
    """Результат заказа номера от SMS сервиса"""
    success: bool
    phone_number: Optional[str] = None
    external_order_id: Optional[str] = None
    error_message: Optional[str] = None
    balance: Optional[float] = None

@dataclass
class SMSStatusResult:
    """Результат проверки статуса заказа"""
    success: bool
    status: str  # waiting, received, expired, cancelled
    message_text: Optional[str] = None
    code: Optional[str] = None
    error_message: Optional[str] = None

class SMSAdapter(ABC):
    """Абстрактный адаптер для работы с SMS сервисами"""
    
    def __init__(self, api_key: str, api_url: str, **kwargs):
        self.api_key = api_key
        self.api_url = api_url
        self.config = kwargs
        
    @abstractmethod
    async def get_balance(self) -> float:
        """Получить баланс аккаунта"""
        pass
    
    @abstractmethod
    async def get_available_numbers(self, country_code: str, service_code: str) -> int:
        """Получить количество доступных номеров"""
        pass
    
    @abstractmethod
    async def order_number(self, country_code: str, service_code: str) -> SMSOrderResult:
        """Заказать номер телефона"""
        pass
    
    @abstractmethod
    async def get_sms(self, external_order_id: str) -> SMSStatusResult:
        """Получить SMS по ID заказа"""
        pass
    
    @abstractmethod
    async def cancel_order(self, external_order_id: str) -> bool:
        """Отменить заказ"""
        pass
    
    @abstractmethod
    async def get_order_status(self, external_order_id: str) -> str:
        """Получить статус заказа"""
        pass
    
    def extract_code_from_message(self, message_text: str) -> Optional[str]:
        """Извлечь код из SMS сообщения"""
        import re
        
        # Паттерны для поиска кода
        patterns = [
            r'\b(\d{4,6})\b',  # 4-6 цифр подряд
            r'код:?\s*(\d+)',  # "код: 12345"
            r'code:?\s*(\d+)',  # "code: 12345"
            r'verification:?\s*(\d+)',  # "verification: 12345"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                code = match.group(1)
                if 4 <= len(code) <= 6:  # Фильтруем по длине
                    return code
        
        return None
    
    def map_service_name_to_code(self, service_name: str) -> str:
        """Преобразовать название сервиса в код для API"""
        mapping = {
            "telegram": "tg",
            "whatsapp": "wa", 
            "discord": "ds",
            "viber": "vi",
            "signal": "sg"
        }
        return mapping.get(service_name.lower(), service_name.lower())
    
    def map_country_code(self, country_code: str) -> str:
        """Преобразовать код страны в формат SMS сервиса"""
        # Большинство сервисов используют стандартные коды
        return country_code.lower()

class SMSProviderFactory:
    """Фабрика для создания SMS провайдеров"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        """Зарегистрировать провайдера"""
        cls._providers[name] = provider_class
        logger.info(f"Registered SMS provider: {name}")
    
    @classmethod
    def create_provider(cls, provider_name: str, **config) -> SMSAdapter:
        """Создать экземпляр провайдера"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown SMS provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Получить список доступных провайдеров"""
        return list(cls._providers.keys())