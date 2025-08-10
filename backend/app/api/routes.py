from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import logging
import json
import uuid
from datetime import datetime, timedelta

from ..core.database import get_async_db
from ..models.models import Country, Service, User, Order
from ..services.user_service import UserService
from ..services.order_service import OrderService
from ..schemas.schemas import OrderCreate, OrderStatus

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/countries")
async def get_countries(db: AsyncSession = Depends(get_async_db)) -> List[Dict[str, Any]]:
    """Получить список доступных стран из БД"""
    try:
        logger.info("Getting countries list from database")
        result = await db.execute(select(Country))
        countries = result.scalars().all()
        
        countries_data = [
            {
                "id": country.id,
                "name": country.name,
                "code": country.code,
                "flag": country.flag,
                "priceFrom": country.price_from,
                "available": country.available,
                "numbersCount": country.numbers_count,
                "status": country.status
            }
            for country in countries
        ]
        
        logger.info(f"Returning {len(countries_data)} countries from DB")
        return countries_data
        
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/services")
async def get_services(db: AsyncSession = Depends(get_async_db)) -> List[Dict[str, Any]]:
    """Получить список доступных сервисов из БД"""
    try:
        logger.info("Getting services list from database")
        result = await db.execute(select(Service))
        services = result.scalars().all()
        
        services_data = [
            {
                "id": service.id,
                "name": service.name,
                "icon": service.icon,
                "priceFrom": service.price_from,
                "priceTo": service.price_to,
                "available": service.available
            }
            for service in services
        ]
        
        logger.info(f"Returning {len(services_data)} services from DB")
        return services_data
        
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    """Получить пользователя или создать автоматически"""
    try:
        logger.info(f"Getting user info for: {user_id}")
        
        # Ищем пользователя
        user = await UserService.get_user_by_telegram_id(db, user_id)
        
        if not user:
            # Пользователь не найден - создаем автоматически
            logger.info(f"User not found, creating: {user_id}")
            
            from ..schemas.schemas import UserCreate
            
            # Определяем имя пользователя
            display_name = "User"
            username = None
            
            # Если это числовой ID (реальный Telegram ID)
            if user_id.isdigit():
                username = f"user_{user_id}"
                display_name = "Telegram User"
            elif user_id == "sample_user":
                username = "sample_user"
                display_name = "Sample User"
            else:
                username = user_id
                display_name = user_id.title()
            
            user_data = UserCreate(
                telegram_id=user_id,
                username=username,
                first_name=display_name,
                last_name=None,
                balance=0,  # Новый пользователь с нулевым балансом
                is_admin=False
            )
            
            user = await UserService.create_user(db, user_data)
            
            if user:
                logger.info(f"✅ Auto-created user: {user_id}")
            else:
                logger.error(f"❌ Failed to create user: {user_id}")
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Получаем заказы пользователя
        orders_result = await db.execute(
            select(Order).where(Order.user_telegram_id == user_id)
        )
        orders = orders_result.scalars().all()
        
        return {
            "id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance": user.balance / 100,  # Конвертируем копейки в рубли
            "is_admin": user.is_admin,
            "orders": [
                {
                    "id": order.id,
                    "status": order.status,
                    "phone_number": order.phone_number,
                    "created_at": order.created_at.isoformat()
                }
                for order in orders
            ],
            "created_at": user.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting/creating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders")
async def get_orders(
    user_id: str = None, 
    db: AsyncSession = Depends(get_async_db)
) -> List[Dict[str, Any]]:
    """Получить список заказов пользователя из БД"""
    try:
        logger.info(f"Getting orders for user: {user_id}")
        
        if not user_id:
            return []
        
        # Получаем заказы с связанными данными
        query = (
            select(Order, Country, Service)
            .join(Country, Order.country_id == Country.id)
            .join(Service, Order.service_id == Service.id)
            .where(Order.user_telegram_id == user_id)
            .order_by(Order.created_at.desc())
        )
        
        result = await db.execute(query)
        orders_data = []
        
        for order, country, service in result:
            orders_data.append({
                "id": order.id,
                "phone_number": order.phone_number,
                "country": {
                    "id": country.id,
                    "name": country.name,
                    "flag": country.flag
                },
                "service": {
                    "id": service.id,
                    "name": service.name,
                    "icon": service.icon
                },
                "price": order.price,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "expires_at": order.expires_at.isoformat()
            })
        
        logger.info(f"Returning {len(orders_data)} orders from DB")
        return orders_data
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/orders")
async def create_order(
    request: Request, 
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Создать новый заказ в БД"""
    try:
        # Читаем данные запроса
        body = await request.body()
        logger.info(f"Raw request body: {body}")
        
        try:
            order_data_raw = json.loads(body) if body else {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        logger.info(f"Parsed order data: {order_data_raw}")
        
        # Извлекаем и валидируем данные
        user_id = order_data_raw.get("user_id", order_data_raw.get("userId", "sample_user"))
        country_id = order_data_raw.get("country_id", order_data_raw.get("countryId"))
        service_id = order_data_raw.get("service_id", order_data_raw.get("serviceId"))
        
        if not country_id or not service_id:
            raise HTTPException(status_code=400, detail="Missing country_id or service_id")
        
        # Создаем заказ через сервис
        order_service = OrderService()
        order_create = OrderCreate(
            country_id=country_id,
            service_id=service_id,
            telegram_id=user_id
        )
        
        order = await order_service.create_order(db, order_create)
        
        if not order:
            raise HTTPException(status_code=400, detail="Failed to create order")
        
        # Возвращаем созданный заказ
        return {
            "success": True,
            "id": order.id,
            "user_id": order.user_telegram_id,
            "country_id": order.country_id,
            "service_id": order.service_id,
            "phone_number": order.phone_number,
            "status": order.status,
            "cost": order.price / 100,  # Конвертируем копейки в рубли
            "created_at": order.created_at.isoformat(),
            "expires_at": order.expires_at.isoformat(),
            "messages": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders/{order_id}")
async def get_order(
    order_id: str, 
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Получить информацию о заказе из БД"""
    try:
        logger.info(f"Getting order: {order_id}")
        
        # Получаем заказ с связанными данными
        query = (
            select(Order, Country, Service)
            .join(Country, Order.country_id == Country.id)
            .join(Service, Order.service_id == Service.id)
            .where(Order.id == order_id)
        )
        
        result = await db.execute(query)
        order_data = result.first()
        
        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order, country, service = order_data
        
        # Получаем сообщения заказа
        from ..models.models import Message
        messages_result = await db.execute(
            select(Message).where(Message.order_id == order_id)
        )
        messages = messages_result.scalars().all()
        
        return {
            "id": order.id,
            "user_id": order.user_telegram_id,
            "country": {
                "id": country.id,
                "name": country.name,
                "flag": country.flag
            },
            "service": {
                "id": service.id,
                "name": service.name,
                "icon": service.icon
            },
            "phone_number": order.phone_number,
            "status": order.status,
            "cost": order.price / 100,
            "created_at": order.created_at.isoformat(),
            "expires_at": order.expires_at.isoformat(),
            "messages": [
                {
                    "id": msg.id,
                    "text": msg.text,
                    "code": msg.code,
                    "received_at": msg.received_at.isoformat()
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Отменить заказ в БД"""
    try:
        logger.info(f"Cancelling order: {order_id}")
        
        # Получаем заказ
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != OrderStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Order cannot be cancelled")
        
        # Отменяем через сервис
        order_service = OrderService()
        success = await order_service.cancel_order(db, order_id, order.user_telegram_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel order")
        
        return {
            "id": order_id,
            "status": "cancelled",
            "message": "Order cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/countries/{country_id}/services")
async def get_services_by_country(
    country_id: str, 
    db: AsyncSession = Depends(get_async_db)
) -> List[Dict[str, Any]]:
    """Получить список сервисов для определенной страны"""
    try:
        logger.info(f"Getting services for country: {country_id}")
        
        # Проверяем что страна существует
        country_result = await db.execute(
            select(Country).where(Country.id == country_id)
        )
        country = country_result.scalars().first()
        
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        # Возвращаем все доступные сервисы
        services_result = await db.execute(
            select(Service).where(Service.available == True)
        )
        services = services_result.scalars().all()
        
        services_data = [
            {
                "id": service.id,
                "name": service.name,
                "icon": service.icon,
                "priceFrom": max(service.price_from, country.price_from),
                "priceTo": service.price_to,
                "available": service.available
            }
            for service in services
        ]
        
        logger.info(f"Returning {len(services_data)} services for country {country_id}")
        return services_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting services for country {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/prices")
async def get_prices(db: AsyncSession = Depends(get_async_db)) -> List[Dict[str, Any]]:
    """Получить список цен для стран/сервисов из БД"""
    try:
        logger.info("Getting prices list from database")
        
        # Получаем все комбинации стран и сервисов
        query = select(Country, Service).where(
            Country.available == True,
            Service.available == True
        )
        
        result = await db.execute(query)
        prices_data = []
        
        for country, service in result:
            price = max(country.price_from, service.price_from)
            prices_data.append({
                "country_id": country.id,
                "service_id": service.id,
                "price": price
            })
        
        logger.info(f"Returning {len(prices_data)} prices from DB")
        return prices_data
        
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Проверка состояния API"""
    return {
        "status": "ok",
        "message": "OnlineSim API is running",
        "version": "1.0.0"
    }

# Добавить в конец app/api/routes.py

@router.get("/orders/{order_id}/messages")
async def get_order_messages(
    order_id: str,
    db: AsyncSession = Depends(get_async_db)
) -> List[Dict[str, Any]]:
    """Получить SMS сообщения заказа"""
    try:
        from ..models.models import Message
        
        messages_result = await db.execute(
            select(Message)
            .where(Message.order_id == order_id)
            .order_by(Message.received_at.asc())
        )
        messages = messages_result.scalars().all()
        
        return [
            {
                "id": message.id,
                "text": message.text,
                "code": message.code,
                "received_at": message.received_at.isoformat(),
                "has_code": bool(message.code)
            }
            for message in messages
        ]
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook/sms")
async def sms_webhook(request: Request) -> Dict[str, Any]:
    """Webhook для получения SMS"""
    try:
        body = await request.body()
        webhook_data = json.loads(body) if body else {}
        
        from ..services.sms.webhook import webhook_handler
        success = await webhook_handler.process_webhook(webhook_data)
        
        return {"status": "ok"} if success else {"status": "error"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook failed")
    
# ===== Дополнительные эндпоинты =====

@router.get("/messages")
async def get_user_messages(
    user_id: str = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Получить все сообщения пользователя с пагинацией"""
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        logger.info(f"Getting messages for user: {user_id}, limit: {limit}, offset: {offset}")
        
        from ..models.models import Message
        
        # Получаем сообщения через заказы пользователя с пагинацией
        query = (
            select(Message, Order, Country, Service)
            .join(Order, Message.order_id == Order.id)
            .join(Country, Order.country_id == Country.id)
            .join(Service, Order.service_id == Service.id)
            .where(Order.user_telegram_id == user_id)
            .order_by(Message.received_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(query)
        messages_data = []
        
        for message, order, country, service in result:
            messages_data.append({
                "id": message.id,
                "order_id": message.order_id,
                "phone_number": order.phone_number,
                "text": message.text,
                "code": message.code,
                "received_at": message.received_at.isoformat(),
                "has_code": bool(message.code),
                "order_status": order.status,
                "country": {
                    "name": country.name,
                    "flag": country.flag
                },
                "service": {
                    "name": service.name,
                    "icon": service.icon
                }
            })
        
        # Получаем общий счетчик для пагинации
        count_query = (
            select(Message)
            .join(Order, Message.order_id == Order.id)
            .where(Order.user_telegram_id == user_id)
        )
        count_result = await db.execute(count_query)
        total_count = len(count_result.scalars().all())
        
        logger.info(f"Returning {len(messages_data)} messages out of {total_count}")
        
        return {
            "messages": messages_data,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook/sms/{provider}")
async def sms_webhook_provider(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Webhook для конкретного SMS провайдера"""
    try:
        logger.info(f"SMS webhook from provider: {provider}")
        
        # Проверяем webhook secret если нужно
        webhook_secret = request.headers.get("X-Webhook-Secret")
        # if webhook_secret != settings.sms_webhook_secret:
        #     raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
        body = await request.body()
        logger.info(f"Webhook data from {provider}: {body}")
        
        try:
            webhook_data = json.loads(body) if body else {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {provider}: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Обрабатываем через webhook handler
        from ..services.sms.webhook import webhook_handler
        
        success = await webhook_handler.handle_provider_specific_webhook(provider, webhook_data)
        
        if success:
            return {
                "status": "ok", 
                "message": f"Webhook from {provider} processed successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing {provider} webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders/{order_id}/status")
async def get_order_status(
    order_id: str,
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Получить актуальный статус заказа"""
    try:
        logger.info(f"Getting status for order: {order_id}")
        
        # Получаем заказ
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Получаем количество сообщений
        from ..models.models import Message
        messages_result = await db.execute(
            select(Message).where(Message.order_id == order_id)
        )
        messages = messages_result.scalars().all()
        
        # Проверяем не истек ли заказ
        is_expired = datetime.now() > order.expires_at
        
        return {
            "order_id": order.id,
            "status": order.status,
            "phone_number": order.phone_number,
            "created_at": order.created_at.isoformat(),
            "expires_at": order.expires_at.isoformat(),
            "is_expired": is_expired,
            "messages_count": len(messages),
            "has_sms": len(messages) > 0,
            "latest_code": messages[-1].code if messages and messages[-1].code else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/users/{user_id}/balance")
async def update_user_balance(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Обновить баланс пользователя (админская функция)"""
    try:
        # TODO: Добавить проверку прав администратора
        
        body = await request.body()
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        new_balance = data.get("balance")
        if new_balance is None:
            raise HTTPException(status_code=400, detail="balance is required")
        
        # Конвертируем рубли в копейки
        balance_kopecks = int(float(new_balance) * 100)
        
        # Обновляем баланс
        updated_user = await UserService.update_user_balance(db, user_id, balance_kopecks)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Updated balance for user {user_id}: {balance_kopecks} kopecks")
        
        return {
            "user_id": updated_user.telegram_id,
            "old_balance": data.get("old_balance", 0),
            "new_balance": updated_user.balance / 100,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user balance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary")
async def get_stats_summary(db: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    """Получить общую статистику системы"""
    try:
        logger.info("Getting system stats summary")
        
        # Получаем общую статистику
        from sqlalchemy import func
        
        # Общее количество пользователей
        users_result = await db.execute(select(func.count(User.id)))
        total_users = users_result.scalar()
        
        # Общее количество заказов
        orders_result = await db.execute(select(func.count(Order.id)))
        total_orders = orders_result.scalar()
        
        # Активные заказы
        active_orders_result = await db.execute(
            select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING.value)
        )
        active_orders = active_orders_result.scalar()
        
        # Общий доход (в рублях)
        revenue_result = await db.execute(
            select(func.sum(Order.price)).where(
                Order.status.in_([OrderStatus.RECEIVED.value, OrderStatus.EXPIRED.value])
            )
        )
        total_revenue_kopecks = revenue_result.scalar() or 0
        
        # Сообщения за сегодня
        from ..models.models import Message
        today = datetime.now().date()
        messages_today_result = await db.execute(
            select(func.count(Message.id)).where(
                func.date(Message.received_at) == today
            )
        )
        messages_today = messages_today_result.scalar()
        
        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "active_orders": active_orders,
            "total_revenue": total_revenue_kopecks / 100,
            "messages_today": messages_today,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders/{order_id}/refresh")
async def refresh_order_status(
    order_id: str,
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Принудительно обновить статус заказа через SMS провайдера"""
    try:
        logger.info(f"Refreshing order status: {order_id}")
        
        # Получаем заказ
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != OrderStatus.PENDING.value:
            return {
                "order_id": order.id,
                "status": order.status,
                "message": "Order is not pending"
            }
        
        # Проверяем SMS через провайдера
        order_service = OrderService()
        if order_service.sms_provider and order.external_order_id:
            try:
                sms_result = await order_service.sms_provider.get_sms(order.external_order_id)
                
                if sms_result and sms_result.get('messages'):
                    # Если есть новые сообщения, обрабатываем их
                    for msg in sms_result['messages']:
                        webhook_data = {
                            "order_id": order.external_order_id,
                            "phone_number": order.phone_number,
                            "message_text": msg.get('text', ''),
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        from ..services.sms.webhook import webhook_handler
                        await webhook_handler.process_webhook(webhook_data, "refresh")
                
                return {
                    "order_id": order.id,
                    "status": "refreshed",
                    "messages_found": len(sms_result.get('messages', [])) if sms_result else 0
                }
                
            except Exception as e:
                logger.warning(f"Error refreshing from SMS provider: {e}")
                return {
                    "order_id": order.id,
                    "status": "error",
                    "message": "Failed to refresh from provider"
                }
        
        return {
            "order_id": order.id,
            "status": "no_provider",
            "message": "SMS provider not available"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing order status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")