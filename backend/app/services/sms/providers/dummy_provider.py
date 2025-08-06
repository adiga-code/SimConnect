import asyncio
import random
from datetime import datetime
from typing import Optional
import logging
from ..adapter import SMSAdapter, SMSOrderResult, SMSStatusResult, SMSProviderFactory

logger = logging.getLogger(__name__)

class DummyProvider(SMSAdapter):
    """Заглушка SMS провайдера для тестирования"""
    
    def __init__(self, **kwargs):
        super().__init__("dummy_api_key", "http://dummy-api.com", **kwargs)
        self.balance = 1000.0
        self.orders = {}  # Хранилище заказов
        logger.info("Initialized Dummy SMS Provider")
    
    async def get_balance(self) -> float:
        """Возвращает тестовый баланс"""
        await asyncio.sleep(0.1)  # Имитация задержки API
        logger.info(f"Balance requested: {self.balance}")
        return self.balance
    
    async def get_available_numbers(self, country_code: str, service_code: str) -> int:
        """Возвращает случайное количество номеров"""
        await asyncio.sleep(0.1)
        
        # Имитируем разное количество номеров для разных стран
        counts = {
            "ru": random.randint(100, 1000),
            "ua": random.randint(50, 500), 
            "kz": random.randint(10, 100),
            "us": 0  # США недоступны
        }
        
        count = counts.get(country_code.lower(), random.randint(1, 50))
        logger.info(f"Available numbers for {country_code}/{service_code}: {count}")
        return count
    
    async def order_number(self, country_code: str, service_code: str) -> SMSOrderResult:
        """Имитирует заказ номера"""
        await asyncio.sleep(0.2)
        
        # Имитируем недоступность некоторых стран
        if country_code.lower() == "us":
            return SMSOrderResult(
                success=False,
                error_message="Country not available"
            )
        
        # Генерируем тестовый номер
        phone_patterns = {
            "ru": f"+7 916 {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
            "ua": f"+380 {random.randint(50, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
            "kz": f"+7 {random.randint(700, 799)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
        }
        
        phone_number = phone_patterns.get(country_code.lower(), f"+{random.randint(1, 999)} {random.randint(1000000, 9999999)}")
        external_order_id = f"dummy_{random.randint(100000, 999999)}"
        
        # Сохраняем заказ
        self.orders[external_order_id] = {
            "phone_number": phone_number,
            "country_code": country_code,
            "service_code": service_code,
            "status": "waiting",
            "created_at": datetime.now(),
            "message_text": None,
            "code": None
        }
        
        # Уменьшаем баланс
        price = random.randint(15, 50)
        self.balance -= price
        
        logger.info(f"Ordered number: {phone_number} (ID: {external_order_id})")
        
        return SMSOrderResult(
            success=True,
            phone_number=phone_number,
            external_order_id=external_order_id,
            balance=self.balance
        )
    
    async def get_sms(self, external_order_id: str) -> SMSStatusResult:
        """Имитирует получение SMS"""
        await asyncio.sleep(0.1)
        
        if external_order_id not in self.orders:
            return SMSStatusResult(
                success=False,
                status="not_found",
                error_message="Order not found"
            )
        
        order = self.orders[external_order_id]
        
        # Имитируем получение SMS через случайное время
        elapsed_minutes = (datetime.now() - order["created_at"]).total_seconds() / 60
        
        if order["status"] == "waiting" and elapsed_minutes > random.uniform(1, 5):
            # Генерируем тестовое SMS
            codes = ["12345", "67890", "54321", "98765", "11111"]
            services_messages = {
                "tg": f"Telegram code: {random.choice(codes)}",
                "wa": f"WhatsApp code: {random.choice(codes)}", 
                "ds": f"Discord verification code: {random.choice(codes)}"
            }
            
            message_text = services_messages.get(
                order["service_code"], 
                f"Verification code: {random.choice(codes)}"
            )
            
            code = self.extract_code_from_message(message_text)
            
            order["status"] = "received"
            order["message_text"] = message_text
            order["code"] = code
            
            logger.info(f"SMS received for order {external_order_id}: {message_text}")
            
            return SMSStatusResult(
                success=True,
                status="received",
                message_text=message_text,
                code=code
            )
        
        # Проверяем истечение времени
        if elapsed_minutes > 15:
            order["status"] = "expired"
            return SMSStatusResult(
                success=True,
                status="expired"
            )
        
        return SMSStatusResult(
            success=True,
            status=order["status"]
        )
    
    async def cancel_order(self, external_order_id: str) -> bool:
        """Имитирует отмену заказа"""
        await asyncio.sleep(0.1)
        
        if external_order_id in self.orders:
            order = self.orders[external_order_id]
            if order["status"] == "waiting":
                order["status"] = "cancelled"
                # Возвращаем деньги
                self.balance += random.randint(15, 50)
                logger.info(f"Order {external_order_id} cancelled, balance restored")
                return True
        
        return False
    
    async def get_order_status(self, external_order_id: str) -> str:
        """Получить статус заказа"""
        await asyncio.sleep(0.1)
        
        if external_order_id not in self.orders:
            return "not_found"
        
        return self.orders[external_order_id]["status"]

# Регистрируем провайдера
SMSProviderFactory.register_provider("dummy", DummyProvider)