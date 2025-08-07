from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class SMSOrderResult:
    """Результат заказа номера"""
    success: bool
    order_id: Optional[str] = None
    phone_number: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SMSStatusResult:
    """Результат проверки статуса SMS"""
    success: bool
    status: Optional[str] = None  # pending, received, expired
    messages: Optional[list] = None
    error_message: Optional[str] = None

class BaseSMSProvider(ABC):
    """Базовый класс для SMS провайдеров"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def get_number(self, country_id: str, service_id: str) -> Optional[Dict[str, Any]]:
        """Получить номер телефона"""
        pass
    
    @abstractmethod
    async def get_sms(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Получить SMS сообщения"""
        pass
    
    @abstractmethod
    async def cancel_number(self, order_id: str) -> bool:
        """Отменить номер"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Optional[float]:
        """Получить баланс"""
        pass
    
    @abstractmethod
    async def get_countries(self) -> Optional[Dict[str, Any]]:
        """Получить список стран"""
        pass
    
    @abstractmethod
    async def get_services(self) -> Optional[Dict[str, Any]]:
        """Получить список сервисов"""
        pass