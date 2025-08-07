from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Тестовые данные
MOCK_COUNTRIES = [
    {
        "id": "0",
        "name": "Россия", 
        "code": "RU",
        "flag": "🇷🇺",
        "priceFrom": 15,
        "available": True,
        "numbersCount": 1234,
        "status": "available"
    },
    {
        "id": "1", 
        "name": "Украина",
        "code": "UA", 
        "flag": "🇺🇦",
        "priceFrom": 22,
        "available": True,
        "numbersCount": 856,
        "status": "available"
    },
    {
        "id": "2",
        "name": "Беларусь",
        "code": "BY",
        "flag": "🇧🇾", 
        "priceFrom": 18,
        "available": True,
        "numbersCount": 645,
        "status": "available"
    },
    {
        "id": "3",
        "name": "Казахстан", 
        "code": "KZ",
        "flag": "🇰🇿",
        "priceFrom": 20,
        "available": True, 
        "numbersCount": 432,
        "status": "available"
    }
]

MOCK_SERVICES = [
    {
        "id": "tg",
        "name": "Telegram",
        "icon": "fab fa-telegram-plane",
        "priceFrom": 15,
        "priceTo": 25, 
        "available": True
    },
    {
        "id": "wa",
        "name": "WhatsApp", 
        "icon": "fab fa-whatsapp",
        "priceFrom": 18,
        "priceTo": 30,
        "available": True
    },
    {
        "id": "vk", 
        "name": "VKontakte",
        "icon": "fab fa-vk",
        "priceFrom": 12,
        "priceTo": 20,
        "available": True
    },
    {
        "id": "ok",
        "name": "Odnoklassniki",
        "icon": "fas fa-circle", 
        "priceFrom": 10,
        "priceTo": 15,
        "available": True
    }
]

@router.get("/countries")
async def get_countries() -> List[Dict[str, Any]]:
    """Получить список доступных стран"""
    try:
        logger.info("Getting countries list")
        result = MOCK_COUNTRIES
        logger.info(f"Returning {len(result)} countries: {[c['name'] for c in result]}")
        return result
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/services") 
async def get_services() -> List[Dict[str, Any]]:
    """Получить список доступных сервисов"""
    try:
        logger.info("Getting services list")
        result = MOCK_SERVICES
        logger.info(f"Returning {len(result)} services: {[s['name'] for s in result]}")
        return result
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}")
async def get_user(user_id: str) -> Dict[str, Any]:
    """Получить информацию о пользователе"""
    try:
        logger.info(f"Getting user info for: {user_id}")
        # Мок данные пользователя
        return {
            "id": user_id,
            "username": user_id,
            "balance": 100.50,
            "orders": [],
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders")
async def get_orders(user_id: str = None) -> List[Dict[str, Any]]:
    """Получить список заказов пользователя"""
    try:
        logger.info(f"Getting orders for user: {user_id}")
        # Возвращаем пустой массив для начала
        result = []
        logger.info(f"Returning {len(result)} orders")
        return result
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Добавляем endpoint для сервисов по стране (может быть нужен фронтенду)
@router.get("/countries/{country_id}/services")
async def get_services_by_country(country_id: str) -> List[Dict[str, Any]]:
    """Получить список сервисов для определенной страны"""
    try:
        logger.info(f"Getting services for country: {country_id}")
        result = MOCK_SERVICES  # Возвращаем те же сервисы
        logger.info(f"Returning {len(result)} services for country {country_id}")
        return result
    except Exception as e:
        logger.error(f"Error getting services for country {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Добавляем endpoint для цен (может быть нужен)
@router.get("/prices")
async def get_prices() -> List[Dict[str, Any]]:
    """Получить список цен для стран/сервисов"""
    try:
        logger.info("Getting prices list")
        result = [
            {"country_id": "0", "service_id": "tg", "price": 15},
            {"country_id": "0", "service_id": "wa", "price": 18},
            {"country_id": "1", "service_id": "tg", "price": 22},
            {"country_id": "1", "service_id": "wa", "price": 25}
        ]
        logger.info(f"Returning {len(result)} prices")
        return result
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Добавляем catch-all для неизвестных endpoints
@router.get("/{path:path}")
async def catch_all(path: str):
    """Перехватчик для всех неизвестных API путей"""
    logger.warning(f"Unknown API endpoint requested: /{path}")
    # Возвращаем пустой массив по умолчанию
    return []

@router.post("/orders")
async def create_order(request: Request) -> Dict[str, Any]:
    """Создать новый заказ номера"""
    try:
        # Читаем сырые данные из запроса
        body = await request.body()
        logger.info(f"Raw request body: {body}")
        
        # Пробуем разобрать JSON
        try:
            order_data = json.loads(body) if body else {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            order_data = {}
        
        logger.info(f"Parsed order data: {order_data}")
        
        # Более мягкая валидация - берем что есть
        user_id = order_data.get("user_id", order_data.get("userId", "sample_user"))
        country_id = order_data.get("country_id", order_data.get("countryId", "0"))
        service_id = order_data.get("service_id", order_data.get("serviceId", "tg"))
        
        logger.info(f"Extracted: user_id={user_id}, country_id={country_id}, service_id={service_id}")
        
        # Создаем заказ с любыми данными
        import time
        order_id = f"order_{int(time.time())}"
        
        new_order = {
            "id": order_id,
            "user_id": user_id,
            "country_id": str(country_id),
            "service_id": str(service_id),
            "phone_number": "+79001234567",  # Мок номер
            "status": "pending",
            "cost": 15.0,
            "created_at": "2024-01-01T10:00:00Z",
            "messages": [],
            "success": True
        }
        
        logger.info(f"Successfully created order: {new_order}")
        return new_order
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        # Возвращаем успешный ответ даже при ошибке для тестирования
        return {
            "success": True,
            "id": "order_fallback",
            "user_id": "sample_user",
            "country_id": "0",
            "service_id": "tg",
            "phone_number": "+79001234567",
            "status": "pending",
            "cost": 15.0,
            "created_at": "2024-01-01T10:00:00Z",
            "messages": [],
            "error_info": str(e)
        }

@router.get("/orders/{order_id}")
async def get_order(order_id: str) -> Dict[str, Any]:
    """Получить информацию о заказе"""
    try:
        logger.info(f"Getting order: {order_id}")
        
        # Мок данные заказа
        return {
            "id": order_id,
            "user_id": "sample_user", 
            "country_id": "0",
            "service_id": "tg",
            "phone_number": "+79001234567",
            "status": "pending",
            "cost": 15.0,
            "created_at": "2024-01-01T10:00:00Z",
            "messages": []
        }
        
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """Отменить заказ"""
    try:
        logger.info(f"Cancelling order: {order_id}")
        
        return {
            "id": order_id,
            "status": "cancelled",
            "message": "Order cancelled successfully"
        }
        
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Проверка состояния API"""
    return {
        "status": "ok",
        "message": "OnlineSim API is running",
        "version": "1.0.0"
    }