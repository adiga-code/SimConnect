from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(String, primary_key=True)
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False, unique=True)
    flag = Column(Text, nullable=False)
    price_from = Column(Integer, nullable=False)
    available = Column(Boolean, nullable=False, default=True)
    numbers_count = Column(Integer, nullable=False, default=0)
    status = Column(Text, nullable=False, default="available")  # available, low, unavailable

class Service(Base):
    __tablename__ = "services"
    
    id = Column(String, primary_key=True)
    name = Column(Text, nullable=False)
    icon = Column(Text, nullable=False)
    price_from = Column(Integer, nullable=False)
    price_to = Column(Integer, nullable=False)
    available = Column(Boolean, nullable=False, default=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    phone_number = Column(Text, nullable=False)
    country_id = Column(String, ForeignKey("countries.id"), nullable=False)
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    user_telegram_id = Column(String, ForeignKey("users.telegram_id"), nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(Text, nullable=False, default="pending")  # pending, received, expired, cancelled
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # SMS service specific fields
    external_order_id = Column(String, nullable=True)  # ID от SMS сервиса
    
    # Relationships
    country = relationship("Country")
    service = relationship("Service")
    user = relationship("User")
    messages = relationship("Message", back_populates="order")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    text = Column(Text, nullable=False)
    code = Column(Text, nullable=True)
    received_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationship
    order = relationship("Order", back_populates="messages")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    telegram_id = Column(String, nullable=False, unique=True, index=True)
    username = Column(Text, nullable=True)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    balance = Column(Integer, nullable=False, default=0)  # in kopecks
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    orders = relationship("Order")

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(String, primary_key=True)
    key = Column(Text, nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class Statistic(Base):
    __tablename__ = "statistics"
    
    id = Column(String, primary_key=True)
    date = Column(Text, nullable=False, unique=True)  # YYYY-MM-DD
    total_orders = Column(Integer, nullable=False, default=0)
    total_revenue = Column(Integer, nullable=False, default=0)  # in kopecks
    new_users = Column(Integer, nullable=False, default=0)
    active_users = Column(Integer, nullable=False, default=0)