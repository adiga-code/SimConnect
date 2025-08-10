import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.models import User
from ..schemas.schemas import UserCreate
from ..utils.telegram import validate_telegram_init_data

logger = logging.getLogger(__name__)

class UserService:
    """Сервис для работы с пользователями (async)"""
    
    @staticmethod
    async def get_user_by_telegram_id(db: AsyncSession, telegram_id: str) -> Optional[User]:
        """Получить пользователя по Telegram ID асинхронно"""
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalars().first()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> Optional[User]:
        """Создать нового пользователя асинхронно"""
        try:
            # Проверяем, не существует ли уже пользователь
            existing_user = await UserService.get_user_by_telegram_id(db, user_data.telegram_id)
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
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"User created: {user.telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def update_user_balance(db: AsyncSession, telegram_id: str, new_balance: int) -> Optional[User]:
        """Обновить баланс пользователя асинхронно"""
        try:
            user = await UserService.get_user_by_telegram_id(db, telegram_id)
            if not user:
                logger.error(f"User not found for balance update: {telegram_id}")
                return None
            
            old_balance = user.balance
            user.balance = new_balance
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"User balance updated: {telegram_id}, {old_balance} -> {new_balance}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user balance: {e}")
            await db.rollback()
            return None
    
    # Остальные методы аналогично с async/await...
    
    @staticmethod
    def _generate_id() -> str:
        """Генерировать уникальный ID"""
        import uuid
        return str(uuid.uuid4())