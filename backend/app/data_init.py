import logging
from sqlalchemy.orm import Session
from .core.database import SessionLocal
from .models.models import Country, Service, User, Setting, Statistic
from .schemas.schemas import CountryStatus
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

async def initialize_data():
    """Инициализировать начальные данные в БД"""
    db = SessionLocal()
    try:
        await _init_countries(db)
        await _init_services(db)
        await _init_sample_user(db)
        await _init_settings(db)
        await _init_statistics(db)
        
        db.commit()
        logger.info("Initial data initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        db.rollback()
    finally:
        db.close()

async def _init_countries(db: Session):
    """Инициализировать страны"""
    if db.query(Country).count() > 0:
        logger.info("Countries already exist, skipping initialization")
        return
    
    countries_data = [
        {
            "name": "Россия",
            "code": "RU", 
            "flag": "🇷🇺",
            "price_from": 15,
            "available": True,
            "numbers_count": 1234,
            "status": CountryStatus.AVAILABLE.value
        },
        {
            "name": "Украина",
            "code": "UA",
            "flag": "🇺🇦", 
            "price_from": 22,
            "available": True,
            "numbers_count": 856,
            "status": CountryStatus.AVAILABLE.value
        },
        {
            "name": "Казахстан",
            "code": "KZ",
            "flag": "🇰🇿",
            "price_from": 18,
            "available": True,
            "numbers_count": 12,
            "status": CountryStatus.LOW.value
        },
        {
            "name": "США",
            "code": "US",
            "flag": "🇺🇸",
            "price_from": 45,
            "available": False,
            "numbers_count": 0,
            "status": CountryStatus.UNAVAILABLE.value
        }
    ]
    
    for country_data in countries_data:
        country = Country(
            id=str(uuid.uuid4()),
            **country_data
        )
        db.add(country)
    
    logger.info(f"Created {len(countries_data)} countries")

async def _init_services(db: Session):
    """Инициализировать сервисы"""
    if db.query(Service).count() > 0:
        logger.info("Services already exist, skipping initialization")
        return
    
    services_data = [
        {
            "name": "Telegram",
            "icon": "fab fa-telegram",
            "price_from": 15,
            "price_to": 25,
            "available": True
        },
        {
            "name": "WhatsApp", 
            "icon": "fab fa-whatsapp",
            "price_from": 18,
            "price_to": 30,
            "available": True
        },
        {
            "name": "Discord",
            "icon": "fab fa-discord",
            "price_from": 20,
            "price_to": 35,
            "available": True
        }
    ]
    
    for service_data in services_data:
        service = Service(
            id=str(uuid.uuid4()),
            **service_data
        )
        db.add(service)
    
    logger.info(f"Created {len(services_data)} services")

async def _init_sample_user(db: Session):
    """Инициализировать тестового пользователя"""
    sample_telegram_id = "sample_user"
    
    existing_user = db.query(User).filter(User.telegram_id == sample_telegram_id).first()
    if existing_user:
        logger.info("Sample user already exists, skipping initialization")
        return
    
    user = User(
        id=str(uuid.uuid4()),
        telegram_id=sample_telegram_id,
        username="testuser",
        first_name="Test",
        last_name="User",
        balance=12550,  # 125.50 рублей в копейках
        is_admin=True
    )
    
    db.add(user)
    logger.info("Created sample user")

async def _init_settings(db: Session):
    """Инициализировать настройки"""
    if db.query(Setting).count() > 0:
        logger.info("Settings already exist, skipping initialization")
        return
    
    settings_data = [
        {
            "key": "commission_percent",
            "value": "5",
            "description": "Комиссия в процентах"
        },
        {
            "key": "min_balance",
            "value": "100", 
            "description": "Минимальный баланс в копейках"
        },
        {
            "key": "support_url",
            "value": "https://t.me/support",
            "description": "Ссылка на техподдержку"
        },
        {
            "key": "telegram_channel",
            "value": "https://t.me/onlinesim_channel",
            "description": "Ссылка на канал Telegram"
        }
    ]
    
    for setting_data in settings_data:
        setting = Setting(
            id=str(uuid.uuid4()),
            updated_at=datetime.now(),
            **setting_data
        )
        db.add(setting)
    
    logger.info(f"Created {len(settings_data)} settings")

async def _init_statistics(db: Session):
    """Инициализировать статистику"""
    if db.query(Statistic).count() > 0:
        logger.info("Statistics already exist, skipping initialization")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = datetime.now().replace(day=datetime.now().day - 1).strftime("%Y-%m-%d")
    
    statistics_data = [
        {
            "date": today,
            "total_orders": 45,
            "total_revenue": 125000,
            "new_users": 12, 
            "active_users": 89
        },
        {
            "date": yesterday,
            "total_orders": 38,
            "total_revenue": 98500,
            "new_users": 8,
            "active_users": 76
        }
    ]
    
    for stat_data in statistics_data:
        statistic = Statistic(
            id=str(uuid.uuid4()),
            **stat_data
        )
        db.add(statistic)
    
    logger.info(f"Created {len(statistics_data)} statistics records")