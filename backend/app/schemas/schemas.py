from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    RECEIVED = "received" 
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class CountryStatus(str, Enum):
    AVAILABLE = "available"
    LOW = "low"
    UNAVAILABLE = "unavailable"

# Base schemas
class CountryBase(BaseModel):
    name: str
    code: str
    flag: str
    price_from: int
    available: bool = True
    numbers_count: int = 0
    status: CountryStatus = CountryStatus.AVAILABLE

class Country(CountryBase):
    id: str
    
    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    name: str
    icon: str
    price_from: int
    price_to: int
    available: bool = True

class Service(ServiceBase):
    id: str
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    phone_number: str
    country_id: str
    service_id: str
    price: int
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(BaseModel):
    country_id: str
    service_id: str
    telegram_id: str

class Order(OrderBase):
    id: str
    user_telegram_id: str
    expires_at: datetime
    created_at: datetime
    external_order_id: Optional[str] = None
    
    # Relationships
    country: Optional[Country] = None
    service: Optional[Service] = None
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    text: str
    code: Optional[str] = None

class MessageCreate(MessageBase):
    order_id: str

class Message(MessageBase):
    id: str
    order_id: str
    received_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    balance: int = 0
    is_admin: bool = False

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    value: str

class Setting(SettingBase):
    id: str
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StatisticBase(BaseModel):
    date: str  # YYYY-MM-DD
    total_orders: int = 0
    total_revenue: int = 0
    new_users: int = 0
    active_users: int = 0

class StatisticCreate(StatisticBase):
    pass

class Statistic(StatisticBase):
    id: str
    
    class Config:
        from_attributes = True

# Response schemas
class OrderResponse(Order):
    messages: List[Message] = []

# Webhook schemas
class SMSWebhookData(BaseModel):
    order_id: str
    phone_number: str
    message_text: str
    code: Optional[str] = None
    timestamp: datetime

# SSE Event schemas  
class SSEEvent(BaseModel):
    type: str
    data: dict

class OrderStatusUpdate(BaseModel):
    order_id: str
    status: OrderStatus
    message: Optional[str] = None

class SMSReceived(BaseModel):
    order_id: str
    message: Message