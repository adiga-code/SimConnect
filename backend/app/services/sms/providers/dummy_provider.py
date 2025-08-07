import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .base_provider import BaseSMSProvider

logger = logging.getLogger(__name__)

class DummyProvider(BaseSMSProvider):
    """Dummy SMS провайдер для тестирования"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.orders = {}  # Хранилище для заказов
        
    async def get_number(self, country_id: str, service_id: str) -> Optional[Dict[str, Any]]:
        """Получить номер телефона"""
        try:
            # Генерируем фейковый номер
            order_id = f"dummy_order_{datetime.now().timestamp():.0f}"
            phone_number = f"+7900{datetime.now().microsecond % 1000000:06d}"
            
            # Сохраняем заказ
            self.orders[order_id] = {
                "phone_number": phone_number,
                "status": "pending",
                "messages": [],
                "created_at": datetime.now()
            }
            
            logger.info(f"Generated dummy number: {phone_number} for order: {order_id}")
            
            return {
                "success": True,
                "order_id": order_id,
                "phone_number": phone_number,
                "cost": 15.0
            }
            
        except Exception as e:
            logger.error(f"Error in dummy get_number: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sms(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Получить SMS сообщения"""
        try:
            if order_id not in self.orders:
                return {
                    "success": False,
                    "error": "Order not found"
                }
            
            order = self.orders[order_id]
            
            # Имитируем получение SMS через некоторое время
            if not order["messages"] and order["status"] == "pending":
                # После 10 секунд добавляем тестовое SMS
                elapsed = (datetime.now() - order["created_at"]).total_seconds()
                if elapsed > 10:
                    test_message = {
                        "text": f"Ваш код подтверждения: {12345}",
                        "received_at": datetime.now().isoformat(),
                        "code": "12345"
                    }
                    order["messages"].append(test_message)
                    order["status"] = "received"
                    
                    logger.info(f"Added dummy SMS to order {order_id}: {test_message['text']}")
            
            return {
                "success": True,
                "status": order["status"],
                "messages": order["messages"],
                "phone_number": order["phone_number"]
            }
            
        except Exception as e:
            logger.error(f"Error in dummy get_sms: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_number(self, order_id: str) -> bool:
        """Отменить номер"""
        try:
            if order_id in self.orders:
                self.orders[order_id]["status"] = "cancelled"
                logger.info(f"Cancelled dummy order: {order_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error in dummy cancel_number: {e}")
            return False
    
    async def get_balance(self) -> Optional[float]:
        """Получить баланс"""
        try:
            # Возвращаем фейковый баланс
            return 100.50
        except Exception as e:
            logger.error(f"Error in dummy get_balance: {e}")
            return None
    
    async def get_countries(self) -> Optional[Dict[str, Any]]:
        """Получить список стран"""
        try:
            countries = {
                "0": {"name": "Россия", "code": "RU", "flag": "🇷🇺", "price": 15},
                "1": {"name": "Украина", "code": "UA", "flag": "🇺🇦", "price": 22},
                "2": {"name": "Беларусь", "code": "BY", "flag": "🇧🇾", "price": 18},
                "3": {"name": "Казахстан", "code": "KZ", "flag": "🇰🇿", "price": 20},
            }
            return countries
            
        except Exception as e:
            logger.error(f"Error in dummy get_countries: {e}")
            return None
    
    async def get_services(self) -> Optional[Dict[str, Any]]:
        """Получить список сервисов"""
        try:
            services = {
                "tg": {"name": "Telegram", "icon": "fab fa-telegram-plane", "price": 15},
                "wa": {"name": "WhatsApp", "icon": "fab fa-whatsapp", "price": 18},
                "vk": {"name": "VKontakte", "icon": "fab fa-vk", "price": 12},
                "ok": {"name": "Odnoklassniki", "icon": "fas fa-circle", "price": 10},
            }
            return services
            
        except Exception as e:
            logger.error(f"Error in dummy get_services: {e}")
            return None