import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.models import Order, Message, User
from ...schemas.schemas import SMSWebhookData, OrderStatus, MessageCreate
from .validator import SMSValidator
from ..order_service import OrderService

logger = logging.getLogger(__name__)

class SMSWebhookHandler:
    """Обработчик вебхуков от SMS сервисов"""
    
    def __init__(self):
        self.order_service = OrderService()
    
    async def process_webhook(self, webhook_data: Dict[str, Any], provider_name: str = "unknown") -> bool:
        """
        Основной метод обработки вебхука
        
        Args:
            webhook_data: Данные от SMS сервиса
            provider_name: Название провайдера
            
        Returns:
            bool: Успешность обработки
        """
        try:
            logger.info(f"Processing webhook from {provider_name}: {webhook_data}")
            
            # Валидируем входящие данные
            validated_data = SMSValidator.validate_webhook_data(webhook_data)
            if not validated_data:
                logger.error("Webhook data validation failed")
                return False
            
            # Получаем сессию БД
            db = next(get_db())
            try:
                return await self._process_validated_webhook(db, validated_data, provider_name)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    async def _process_validated_webhook(self, db: Session, data: SMSWebhookData, provider_name: str) -> bool:
        """Обработать валидированные данные вебхука"""
        
        # Ищем заказ по ID или номеру телефона
        order = await self._find_order(db, data.order_id, data.phone_number)
        if not order:
            logger.warning(f"Order not found for webhook data: {data.order_id}, {data.phone_number}")
            return False
        
        # Проверяем, можно ли обновить заказ
        if not SMSValidator.validate_order_status_transition(order.status, "received"):
            logger.warning(f"Invalid status transition for order {order.id}: {order.status} -> received")
            return False
        
        # Проверяем на дубликаты сообщений
        existing_messages = db.query(Message).filter(Message.order_id == order.id).all()
        if SMSValidator.is_message_duplicate(existing_messages, data.message_text):
            logger.info(f"Duplicate message ignored for order {order.id}")
            return True
        
        # Создаем сообщение
        message_data = MessageCreate(
            order_id=order.id,
            text=data.message_text,
            code=data.code
        )
        
        message = Message(
            id=self._generate_id(),
            order_id=message_data.order_id,
            text=message_data.text,
            code=message_data.code,
            received_at=datetime.now()
        )
        
        # Обновляем статус заказа
        order.status = OrderStatus.RECEIVED.value
        
        # Сохраняем изменения
        db.add(message)
        db.commit()
        db.refresh(message)
        db.refresh(order)
        
        logger.info(f"SMS processed successfully for order {order.id}")
        
        # Отправляем уведомление во фронтенд через SSE
        await self._notify_frontend(order, message)
        
        return True
    
    async def _find_order(self, db: Session, order_id: str, phone_number: str) -> Optional[Order]:
        """Найти заказ по ID или номеру телефона"""
        
        # Сначала ищем по прямому ID
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            return order
        
        # Затем по external_order_id (ID от SMS сервиса)
        order = db.query(Order).filter(Order.external_order_id == order_id).first()
        if order:
            return order
        
        # В крайнем случае по номеру телефона и статусу pending
        order = db.query(Order).filter(
            Order.phone_number == phone_number,
            Order.status == OrderStatus.PENDING.value
        ).first()
        
        return order
    
    async def _notify_frontend(self, order: Order, message: Message):
        """Отправить уведомление во фронтенд через SSE"""
        try:
            from ...api.sse import sse_manager
            
            # Подготавливаем данные для фронтенда
            frontend_data = SMSValidator.prepare_frontend_message(
                order_id=order.id,
                message_text=message.text,
                code=message.code
            )
            
            # Отправляем уведомление пользователю
            await sse_manager.send_to_user(
                user_id=order.user_telegram_id,
                event_type="sms_received",
                data=frontend_data
            )
            
            # Отправляем обновление статуса заказа
            await sse_manager.send_to_user(
                user_id=order.user_telegram_id,
                event_type="order_status_updated",
                data={
                    "order_id": order.id,
                    "status": order.status,
                    "message": "SMS код получен!"
                }
            )
            
            logger.info(f"Frontend notifications sent for order {order.id}")
            
        except Exception as e:
            logger.error(f"Error sending frontend notification: {e}")
    
    def _generate_id(self) -> str:
        """Генерировать уникальный ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def handle_provider_specific_webhook(self, provider_name: str, raw_data: Dict[str, Any]) -> bool:
        """Обработать вебхук от конкретного провайдера"""
        
        # Здесь можно добавить специфическую логику для разных провайдеров
        provider_handlers = {
            "dummy": self._handle_dummy_webhook,
            "smshub": self._handle_smshub_webhook,
            "5sim": self._handle_5sim_webhook,
        }
        
        handler = provider_handlers.get(provider_name, self._handle_generic_webhook)
        return await handler(raw_data)
    
    async def _handle_dummy_webhook(self, raw_data: Dict[str, Any]) -> bool:
        """Обработать вебхук от dummy провайдера"""
        # Dummy провайдер отправляет данные в стандартном формате
        return await self.process_webhook(raw_data, "dummy")
    
    async def _handle_smshub_webhook(self, raw_data: Dict[str, Any]) -> bool:
        """Обработать вебхук от SMSHub"""
        # Преобразуем формат SMSHub в стандартный
        try:
            webhook_data = {
                "order_id": raw_data.get("id"),
                "phone_number": raw_data.get("phone"),
                "message_text": raw_data.get("text"),
                "timestamp": datetime.now()
            }
            return await self.process_webhook(webhook_data, "smshub")
        except Exception as e:
            logger.error(f"Error processing SMSHub webhook: {e}")
            return False
    
    async def _handle_5sim_webhook(self, raw_data: Dict[str, Any]) -> bool:
        """Обработать вебхук от 5sim"""
        # Преобразуем формат 5sim в стандартный
        try:
            webhook_data = {
                "order_id": raw_data.get("order_id"),
                "phone_number": raw_data.get("number"),
                "message_text": raw_data.get("sms"),
                "timestamp": datetime.now()
            }
            return await self.process_webhook(webhook_data, "5sim")
        except Exception as e:
            logger.error(f"Error processing 5sim webhook: {e}")
            return False
    
    async def _handle_generic_webhook(self, raw_data: Dict[str, Any]) -> bool:
        """Обработать вебхук от неизвестного провайдера"""
        logger.warning(f"Using generic webhook handler for data: {raw_data}")
        return await self.process_webhook(raw_data, "generic")

# Глобальный экземпляр для использования в роутах
webhook_handler = SMSWebhookHandler()