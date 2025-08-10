import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..core.config import settings
from ..core.database import get_async_db
from ..models.models import Order, User, Country, Service, Message
from ..schemas.schemas import OrderCreate, OrderStatus
from .sms.adapter import SMSAdapter

logger = logging.getLogger(__name__)

class OrderService:
    """Асинхронный сервис для работы с заказами"""
    
    def __init__(self):
        self.sms_provider = None
        self._init_sms_provider()
    
    def _init_sms_provider(self):
        """Инициализировать SMS провайдера"""
        try:
            self.sms_provider = SMSAdapter(
                provider_name=settings.sms_provider,
                api_key=settings.sms_api_key
            )
            logger.info(f"SMS provider initialized: {settings.sms_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize SMS provider: {e}")
    
    async def create_order(self, db: AsyncSession, order_data: OrderCreate) -> Optional[Order]:
        """Создать новый заказ асинхронно"""
        try:
            # Проверяем пользователя
            user_result = await db.execute(
                select(User).where(User.telegram_id == order_data.telegram_id)
            )
            user = user_result.scalars().first()
            
            if not user:
                logger.error(f"User not found: {order_data.telegram_id}")
                return None
            
            # Проверяем страну и сервис
            country_result = await db.execute(
                select(Country).where(Country.id == order_data.country_id)
            )
            country = country_result.scalars().first()
            
            service_result = await db.execute(
                select(Service).where(Service.id == order_data.service_id)
            )
            service = service_result.scalars().first()
            
            if not country or not service:
                logger.error("Country or service not found")
                return None
            
            if not country.available or not service.available:
                logger.error("Country or service not available")
                return None
            
            # Вычисляем цену
            price = max(country.price_from, service.price_from)
            
            # Проверяем баланс
            if user.balance < price:
                logger.error(f"Insufficient balance: {user.balance} < {price}")
                return None
            
            # Заказываем номер через SMS провайдера
            sms_result = await self._order_phone_number(country.code, service.name)
            if not sms_result or not sms_result.get('success'):
                logger.error(f"Failed to order phone number: {sms_result}")
                return None
            
            # Создаем заказ
            order = Order(
                id=self._generate_id(),
                phone_number=sms_result.get('phone_number', '+79001234567'),
                country_id=order_data.country_id,
                service_id=order_data.service_id,
                user_telegram_id=order_data.telegram_id,
                price=price,
                status=OrderStatus.PENDING.value,
                expires_at=datetime.now() + timedelta(minutes=settings.order_timeout_minutes),
                external_order_id=sms_result.get('order_id')
            )
            
            # Списываем деньги с баланса
            user.balance -= price
            
            # Сохраняем в БД
            db.add(order)
            await db.commit()
            await db.refresh(order)
            
            logger.info(f"Order created: {order.id}, phone: {order.phone_number}")
            
            # Запускаем фоновую задачу для отслеживания истечения времени
            asyncio.create_task(self._monitor_order_expiration(order.id))
            
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            await db.rollback()
            return None
    
    async def cancel_order(self, db: AsyncSession, order_id: str, user_telegram_id: str) -> bool:
        """Отменить заказ асинхронно"""
        try:
            order_result = await db.execute(
                select(Order).where(
                    and_(
                        Order.id == order_id,
                        Order.user_telegram_id == user_telegram_id,
                        Order.status == OrderStatus.PENDING.value
                    )
                )
            )
            order = order_result.scalars().first()
            
            if not order:
                logger.warning(f"Order not found or cannot be cancelled: {order_id}")
                return False
            
            # Отменяем заказ в SMS сервисе
            if order.external_order_id and self.sms_provider:
                try:
                    await self.sms_provider.cancel_number(order.external_order_id)
                except Exception as e:
                    logger.warning(f"Failed to cancel order in SMS service: {e}")
            
            # Возвращаем деньги
            user_result = await db.execute(
                select(User).where(User.telegram_id == user_telegram_id)
            )
            user = user_result.scalars().first()
            
            if user:
                user.balance += order.price
            
            # Обновляем статус
            order.status = OrderStatus.CANCELLED.value
            
            await db.commit()
            logger.info(f"Order cancelled: {order_id}")
            
            # Уведомляем фронтенд
            await self._notify_order_status_change(order, "Заказ отменен")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            await db.rollback()
            return False
    
    async def get_user_orders(self, db: AsyncSession, user_telegram_id: str) -> List[Order]:
        """Получить заказы пользователя асинхронно"""
        result = await db.execute(
            select(Order)
            .where(Order.user_telegram_id == user_telegram_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_active_orders(self, db: AsyncSession) -> List[Order]:
        """Получить активные заказы асинхронно"""
        result = await db.execute(
            select(Order).where(Order.status == OrderStatus.PENDING.value)
        )
        return result.scalars().all()
    
    async def _order_phone_number(self, country_code: str, service_name: str):
        """Заказать номер через SMS провайдера"""
        if not self.sms_provider:
            logger.error("SMS provider not initialized")
            return None
        
        try:
            return await self.sms_provider.get_number(country_code, service_name)
        except Exception as e:
            logger.error(f"Error ordering phone number: {e}")
            return None
    
    async def _monitor_order_expiration(self, order_id: str):
        """Отслеживать истечение времени заказа асинхронно"""
        try:
            # Ждем время истечения заказа
            await asyncio.sleep(settings.order_timeout_minutes * 60)
            
            # Проверяем заказ
            async for db in get_async_db():
                try:
                    order_result = await db.execute(
                        select(Order).where(Order.id == order_id)
                    )
                    order = order_result.scalars().first()
                    
                    if not order:
                        return
                    
                    # Если заказ все еще pending, помечаем как expired и возвращаем деньги
                    if order.status == OrderStatus.PENDING.value:
                        await self._expire_order(db, order)
                        
                finally:
                    await db.close()
                break
                
        except Exception as e:
            logger.error(f"Error monitoring order expiration: {e}")
    
    async def _expire_order(self, db: AsyncSession, order: Order):
        """Пометить заказ как истекший и вернуть деньги асинхронно"""
        try:
            # Возвращаем деньги
            user_result = await db.execute(
                select(User).where(User.telegram_id == order.user_telegram_id)
            )
            user = user_result.scalars().first()
            
            if user:
                user.balance += order.price
            
            # Обновляем статус
            order.status = OrderStatus.EXPIRED.value
            
            # Отменяем заказ в SMS сервисе
            if order.external_order_id and self.sms_provider:
                try:
                    await self.sms_provider.cancel_number(order.external_order_id)
                except Exception as e:
                    logger.warning(f"Failed to cancel expired order in SMS service: {e}")
            
            await db.commit()
            logger.info(f"Order expired: {order.id}")
            
            # Уведомляем фронтенд
            await self._notify_order_status_change(order, "Время ожидания истекло, деньги возвращены")
            
        except Exception as e:
            logger.error(f"Error expiring order: {e}")
            await db.rollback()
    
    async def _notify_order_status_change(self, order: Order, message: str):
        """Уведомить об изменении статуса заказа"""
        try:
            from ..api.sse import sse_manager
            
            await sse_manager.send_to_user(
                user_id=order.user_telegram_id,
                event_type="order_status_updated",
                data={
                    "order_id": order.id,
                    "status": order.status,
                    "message": message
                }
            )
        except Exception as e:
            logger.error(f"Error sending order status notification: {e}")
    
    def _generate_id(self) -> str:
        """Генерировать уникальный ID"""
        import uuid
        return str(uuid.uuid4())

# Асинхронная задача для очистки истекших заказов
class OrderCleanupService:
    """Сервис для очистки истекших заказов"""
    
    @staticmethod
    async def cleanup_expired_orders():
        """Очистить истекшие заказы асинхронно"""
        async for db in get_async_db():
            try:
                expired_orders_result = await db.execute(
                    select(Order).where(
                        and_(
                            Order.status == OrderStatus.PENDING.value,
                            Order.expires_at < datetime.now()
                        )
                    )
                )
                expired_orders = expired_orders_result.scalars().all()
                
                order_service = OrderService()
                for order in expired_orders:
                    await order_service._expire_order(db, order)
                    
                if expired_orders:
                    logger.info(f"Cleaned up {len(expired_orders)} expired orders")
                    
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
            finally:
                await db.close()
            break

# Запускаем периодическую очистку
async def start_cleanup_task():
    """Запустить задачу периодической очистки"""
    while True:
        try:
            await OrderCleanupService.cleanup_expired_orders()
            await asyncio.sleep(60)  # Проверяем каждую минуту
        except Exception as e:
            logger.error(f"Error in cleanup task loop: {e}")
            await asyncio.sleep(60)