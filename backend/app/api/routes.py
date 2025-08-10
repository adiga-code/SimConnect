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
    """Получить информацию о пользователе из БД"""
    try:
        logger.info(f"Getting user info for: {user_id}")
        
        user = await UserService.get_user_by_telegram_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем заказы пользователя
        orders_result = await db.execute(
            select(Order).where(Order.user_telegram_id == user_id)
        )
        orders = orders_result.scalars().all()
        
        return {
            "id": user.telegram_id,
            "username": user.username,
            "balance": user.balance / 100,  # Конвертируем копейки в рубли
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
        logger.error(f"Error getting user {user_id}: {e}")
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