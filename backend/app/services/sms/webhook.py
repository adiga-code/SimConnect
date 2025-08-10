import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.database import get_async_db
from ...models.models import Order, Message, User
from ...schemas.schemas import SMSWebhookData, OrderStatus, MessageCreate
from .validator import SMSValidator

logger = logging.getLogger(__name__)

class SMSWebhookHandler:
    """Асинхронный обработчик вебхуков от SMS сервисов"""
    
    async def process_webhook(self, webhook_data: Dict[str, Any], provider_name: str = "unknown") -> bool:
        """Основной метод обработки вебхука асинхронно"""
        try:
            logger.info(f"Processing webhook from {provider_name}: {webhook_data}")
            
            # Валидируем входящие данные
            validated_data = SMSValidator.validate_webhook_data(webhook_data)
            if not validated_data:
                logger.error("Webhook data validation failed")
                return False
            
            # Получаем асинхронную сессию БД
            async for db in get_async_db():
                try:
                    return await self._process_validated_webhook(db, validated_data, provider_name)
                finally:
                    await db.close()
                break
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    async def _process_validated_webhook(self, db: AsyncSession, data: SMSWebhookData, provider_name: str) -> bool:
        """Обработать валидированные данные вебхука асинхронно"""
        
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
        existing_messages_result = await db.execute(
            select(Message).where(Message.order_id == order.id)
        )
        existing_messages = existing_messages_result.scalars().all()
        
        if SMSValidator.is_message_duplicate(existing_messages, data.message_text):
            logger.info(f"Duplicate message ignored for order {order.id}")
            return True
        
        # Создаем сообщение
        message = Message(
            id=self._generate_id(),
            order_id=order.id,
            text=data.message_text,
            code=data.code,
            received_at=datetime.now()
        )
        
        # Обновляем статус заказа
        order.status = OrderStatus.RECEIVED.value
        
        # Сохраняем изменения
        db.add(message)
        await db.commit()
        await db.refresh(message)
        await db.refresh(order)
        
        logger.info(f"SMS processed successfully for order {order.id}")
        
        # Отправляем уведомление во фронтенд через SSE
        await self._notify_frontend(order, message)
        
        return True
    
    async def _find_order(self, db: AsyncSession, order_id: str, phone_number: str) -> Optional[Order]:
        """Найти заказ по ID или номеру телефона асинхронно"""
        
        # Сначала ищем по прямому ID
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        if order:
            return order
        
        # Затем по external_order_id (ID от SMS сервиса)
        result = await db.execute(select(Order).where(Order.external_order_id == order_id))
        order = result.scalars().first()
        if order:
            return order
        
        # В крайнем случае по номеру телефона и статусу pending
        result = await db.execute(
            select(Order).where(
                Order.phone_number == phone_number,
                Order.status == OrderStatus.PENDING.value
            )
        )
        
        return result.scalars().first()
    
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

# Глобальный экземпляр для использования в роутах
webhook_handler = SMSWebhookHandler()