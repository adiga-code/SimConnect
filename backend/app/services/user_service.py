import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..models.models import User
from ..schemas.schemas import UserCreate
from ..utils.telegram import validate_telegram_init_data

logger = logging.getLogger(__name__)

class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def get_user_by_telegram_id(db: Session, telegram_id: str) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Optional[User]:
        """Создать нового пользователя"""
        try:
            # Проверяем, не существует ли уже пользователь
            existing_user = UserService.get_user_by_telegram_id(db, user_data.telegram_id)
            if existing_user:
                logger.info(f"User already exists: {user_data.telegram_id}")
                return existing_user
            
            # Создаем нового пользователя
            user = User(
                id=UserService._generate_id(),
                telegram_id=user_data.telegram_id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                balance=user_data.balance or 0,
                is_admin=user_data.is_admin or False
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created: {user.telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def update_user_balance(db: Session, telegram_id: str, new_balance: int) -> Optional[User]:
        """Обновить баланс пользователя"""
        try:
            user = UserService.get_user_by_telegram_id(db, telegram_id)
            if not user:
                logger.error(f"User not found for balance update: {telegram_id}")
                return None
            
            old_balance = user.balance
            user.balance = new_balance
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User balance updated: {telegram_id}, {old_balance} -> {new_balance}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user balance: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def add_balance(db: Session, telegram_id: str, amount: int) -> Optional[User]:
        """Добавить деньги к балансу пользователя"""
        try:
            user = UserService.get_user_by_telegram_id(db, telegram_id)
            if not user:
                logger.error(f"User not found for balance addition: {telegram_id}")
                return None
            
            user.balance += amount
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Added {amount} to user balance: {telegram_id}, new balance: {user.balance}")
            return user
            
        except Exception as e:
            logger.error(f"Error adding to user balance: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def subtract_balance(db: Session, telegram_id: str, amount: int) -> Optional[User]:
        """Списать деньги с баланса пользователя"""
        try:
            user = UserService.get_user_by_telegram_id(db, telegram_id)
            if not user:
                logger.error(f"User not found for balance subtraction: {telegram_id}")
                return None
            
            if user.balance < amount:
                logger.warning(f"Insufficient balance for user {telegram_id}: {user.balance} < {amount}")
                return None
            
            user.balance -= amount
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Subtracted {amount} from user balance: {telegram_id}, new balance: {user.balance}")
            return user
            
        except Exception as e:
            logger.error(f"Error subtracting from user balance: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def authenticate_telegram_user(init_data: str) -> Optional[dict]:
        """Аутентифицировать пользователя Telegram WebApp"""
        try:
            # Валидируем данные от Telegram WebApp
            user_data = validate_telegram_init_data(init_data)
            if not user_data:
                logger.warning("Invalid Telegram init data")
                return None
            
            logger.info(f"Telegram user authenticated: {user_data.get('id')}")
            return user_data
            
        except Exception as e:
            logger.error(f"Error authenticating Telegram user: {e}")
            return None
    
    @staticmethod
    def get_or_create_user_from_telegram(db: Session, telegram_user_data: dict) -> Optional[User]:
        """Получить или создать пользователя из данных Telegram"""
        try:
            telegram_id = str(telegram_user_data.get("id"))
            
            # Сначала пытаемся найти существующего пользователя
            user = UserService.get_user_by_telegram_id(db, telegram_id)
            if user:
                # Обновляем данные пользователя, если они изменились
                user.username = telegram_user_data.get("username")
                user.first_name = telegram_user_data.get("first_name")
                user.last_name = telegram_user_data.get("last_name")
                db.commit()
                return user
            
            # Создаем нового пользователя
            user_data = UserCreate(
                telegram_id=telegram_id,
                username=telegram_user_data.get("username"),
                first_name=telegram_user_data.get("first_name"),
                last_name=telegram_user_data.get("last_name"),
                balance=0,  # Новый пользователь начинает с нулевого баланса
                is_admin=False
            )
            
            return UserService.create_user(db, user_data)
            
        except Exception as e:
            logger.error(f"Error getting or creating user from Telegram: {e}")
            return None
    
    @staticmethod
    def set_admin_status(db: Session, telegram_id: str, is_admin: bool) -> Optional[User]:
        """Установить статус администратора"""
        try:
            user = UserService.get_user_by_telegram_id(db, telegram_id)
            if not user:
                logger.error(f"User not found for admin status update: {telegram_id}")
                return None
            
            user.is_admin = is_admin
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Admin status updated for user {telegram_id}: {is_admin}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating admin status: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def format_balance(balance_kopecks: int) -> str:
        """Форматировать баланс для отображения"""
        rubles = balance_kopecks / 100
        return f"₽{rubles:.2f}"
    
    @staticmethod
    def _generate_id() -> str:
        """Генерировать уникальный ID"""
        import uuid
        return str(uuid.uuid4())