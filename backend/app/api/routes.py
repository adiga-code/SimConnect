from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..core.database import get_db
from ..models.models import Country, Service, Order, Message, User, Setting, Statistic
from ..schemas.schemas import (
    Country as CountrySchema, Service as ServiceSchema, 
    Order as OrderSchema, OrderCreate, OrderResponse,
    Message as MessageSchema, User as UserSchema, UserCreate,
    Setting as SettingSchema, SettingUpdate,
    Statistic as StatisticSchema, OrderStatus
)
from ..services.order_service import OrderService
from ..services.user_service import UserService
from ..services.sms.webhook import webhook_handler
from ..utils.telegram import get_current_telegram_user
from .sse import create_sse_response, sse_manager

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

# Dependency для получения текущего пользователя
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    telegram_user = get_current_telegram_user(request)
    if not telegram_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = UserService.get_or_create_user_from_telegram(db, telegram_user)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return user

# Dependency для проверки прав администратора
def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Countries endpoints
@router.get("/countries", response_model=List[CountrySchema])
async def get_countries(db: Session = Depends(get_db)):
    """Получить список стран"""
    return db.query(Country).all()

@router.get("/countries/{country_id}", response_model=CountrySchema)
async def get_country(country_id: str, db: Session = Depends(get_db)):
    """Получить страну по ID"""
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

# Services endpoints
@router.get("/services", response_model=List[ServiceSchema])
async def get_services(db: Session = Depends(get_db)):
    """Получить список сервисов"""
    return db.query(Service).all()

@router.get("/services/{service_id}", response_model=ServiceSchema)
async def get_service(service_id: str, db: Session = Depends(get_db)):
    """Получить сервис по ID"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# Orders endpoints
@router.get("/orders", response_model=List[OrderSchema])
async def get_orders(
    status: Optional[OrderStatus] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить заказы пользователя"""
    query = db.query(Order).filter(Order.user_telegram_id == user.telegram_id)
    
    if status:
        query = query.filter(Order.status == status.value)
    
    return query.order_by(Order.created_at.desc()).all()

@router.post("/orders", response_model=OrderSchema)
async def create_order(
    order_data: OrderCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый заказ"""
    # Устанавливаем telegram_id из аутентифицированного пользователя
    order_data.telegram_id = user.telegram_id
    
    order_service = OrderService()
    order = await order_service.create_order(db, order_data)
    
    if not order:
        raise HTTPException(status_code=400, detail="Failed to create order")
    
    return order

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отменить заказ"""
    order_service = OrderService()
    success = await order_service.cancel_order(db, order_id, user.telegram_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel order")
    
    return {"message": "Order cancelled successfully"}

# Messages endpoints
@router.get("/messages", response_model=List[MessageSchema])
async def get_messages(
    order_id: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить сообщения пользователя"""
    if order_id:
        # Проверяем, что заказ принадлежит пользователю
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_telegram_id == user.telegram_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return db.query(Message).filter(Message.order_id == order_id).order_by(Message.received_at.desc()).all()
    
    # Получаем все сообщения пользователя через его заказы
    user_orders = db.query(Order).filter(Order.user_telegram_id == user.telegram_id).all()
    order_ids = [order.id for order in user_orders]
    
    return db.query(Message).filter(Message.order_id.in_(order_ids)).order_by(Message.received_at.desc()).all()

# Users endpoints
@router.get("/users/{telegram_id}", response_model=UserSchema)
async def get_user(
    telegram_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить пользователя по Telegram ID"""
    # Пользователь может получить только свои данные, админы могут получить любые
    if not current_user.is_admin and current_user.telegram_id != telegram_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("/users", response_model=UserSchema)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Создать пользователя"""
    user = UserService.create_user(db, user_data)
    if not user:
        raise HTTPException(status_code=400, detail="Failed to create user")
    return user

# Settings endpoints (только для админов)
@router.get("/settings", response_model=List[SettingSchema])
async def get_settings(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Получить настройки системы"""
    return db.query(Setting).all()

@router.get("/settings/{key}", response_model=SettingSchema)
async def get_setting(
    key: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Получить настройку по ключу"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/settings/{key}", response_model=SettingSchema)
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Обновить настройку"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.value = setting_data.value
    db.commit()
    db.refresh(setting)
    
    logger.info(f"Setting {key} updated by admin {admin.telegram_id}")
    return setting

# Statistics endpoints (только для админов)
@router.get("/statistics", response_model=List[StatisticSchema])
async def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Получить статистику"""
    query = db.query(Statistic)
    
    if start_date:
        query = query.filter(Statistic.date >= start_date)
    if end_date:
        query = query.filter(Statistic.date <= end_date)
    
    return query.order_by(Statistic.date.desc()).all()

# SSE endpoint
@router.get("/events")
async def events_stream(
    request: Request,
    user: User = Depends(get_current_user)
):
    """Поток Server-Sent Events для пользователя"""
    return create_sse_response(request, user.telegram_id)

# Webhook endpoints
@router.post("/webhook/sms/{provider}")
async def sms_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обработка вебхуков от SMS сервисов"""
    try:
        # Получаем данные из запроса
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            webhook_data = await request.json()
        else:
            # Для form-data
            webhook_data = dict(await request.form())
        
        # Обрабатываем вебхук
        success = await webhook_handler.handle_provider_specific_webhook(provider, webhook_data)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
            
    except Exception as e:
        logger.error(f"Error processing webhook from {provider}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "sse_connections": sse_manager.get_total_connections()
    }

# SSE status endpoint
@router.get("/sse/status")
async def sse_status(user: User = Depends(get_current_user)):
    """Получить статус SSE соединений пользователя"""
    return {
        "user_id": user.telegram_id,
        "connections": sse_manager.get_connection_count(user.telegram_id),
        "total_connections": sse_manager.get_total_connections()
    }