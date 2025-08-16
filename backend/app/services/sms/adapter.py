import logging
from typing import Optional, Dict, Any
from .providers.base_provider import BaseSMSProvider
from .providers.dummy_provider import DummyProvider
from .providers.smsactivate_provider import SMSActivateProvider

logger = logging.getLogger(__name__)

class SMSAdapter:
    """Адаптер для работы с различными SMS провайдерами"""
    
    def __init__(self, provider_name: str = "dummy", api_key: Optional[str] = None):
        self.provider_name = provider_name.lower()
        self.api_key = api_key
        self.provider = self._initialize_provider()
        
    def _initialize_provider(self) -> BaseSMSProvider:
        """Инициализировать SMS провайдера"""
        try:
            if self.provider_name == "dummy":
                logger.info("Initializing dummy SMS provider")
                return DummyProvider(api_key=self.api_key)
            elif self.provider_name == "smsactivate":
                logger.info("Initializing SMSActivate provider")
                return SMSActivateProvider(api_key=self.api_key)
            else:
                logger.error(f"Unknown SMS provider: {self.provider_name}")
                # Возвращаем dummy provider как fallback
                logger.info("Falling back to dummy SMS provider")
                return DummyProvider(api_key=self.api_key)
                
        except Exception as e:
            logger.error(f"Failed to initialize SMS provider {self.provider_name}: {e}")
            # Возвращаем dummy provider как fallback
            logger.info("Falling back to dummy SMS provider")
            return DummyProvider(api_key=self.api_key)
    
    async def get_number(self, country_id: str, service_id: str) -> Optional[Dict[str, Any]]:
        """Получить номер телефона"""
        try:
            return await self.provider.get_number(country_id, service_id)
        except Exception as e:
            logger.error(f"Error getting number: {e}")
            return None
    
    async def get_sms(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Получить SMS сообщения"""
        try:
            return await self.provider.get_sms(order_id)
        except Exception as e:
            logger.error(f"Error getting SMS: {e}")
            return None
    
    async def cancel_number(self, order_id: str) -> bool:
        """Отменить номер"""
        try:
            return await self.provider.cancel_number(order_id)
        except Exception as e:
            logger.error(f"Error cancelling number: {e}")
            return False
    
    async def get_balance(self) -> Optional[float]:
        """Получить баланс"""
        try:
            return await self.provider.get_balance()
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None
    
    async def get_countries(self) -> Optional[Dict[str, Any]]:
        """Получить список стран"""
        try:
            return await self.provider.get_countries()
        except Exception as e:
            logger.error(f"Error getting countries: {e}")
            return None
    
    async def get_services(self) -> Optional[Dict[str, Any]]:
        """Получить список сервисов"""
        try:
            return await self.provider.get_services()
        except Exception as e:
            logger.error(f"Error getting services: {e}")
            return None

# Совместимость со старым кодом
class SMSProviderFactory:
    """Фабрика SMS провайдеров (для совместимости)"""
    
    @staticmethod
    def create_provider(provider_name: str = "dummy", api_key: Optional[str] = None, **kwargs) -> SMSAdapter:
        """Создать SMS провайдера"""
        # Игнорируем лишние kwargs для совместимости
        return SMSAdapter(provider_name=provider_name, api_key=api_key)