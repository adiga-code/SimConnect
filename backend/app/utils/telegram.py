import hashlib
import hmac
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import unquote
from ..core.config import settings

logger = logging.getLogger(__name__)

def validate_telegram_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Валидировать данные инициализации Telegram WebApp
    
    Args:
        init_data: Строка с данными от Telegram WebApp
        
    Returns:
        Dict с данными пользователя или None если валидация не прошла
    """
    try:
        if not init_data or not settings.telegram_bot_token:
            logger.warning("Missing init_data or bot token")
            return None
        
        # Парсим параметры
        params = {}
        for item in init_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                params[key] = unquote(value)
        
        # Извлекаем hash для проверки
        received_hash = params.pop('hash', '')
        if not received_hash:
            logger.warning("No hash in init_data")
            return None
        
        # Создаем строку для проверки
        data_check_string = '\n'.join([
            f"{key}={value}" 
            for key, value in sorted(params.items())
        ])
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            "WebAppData".encode(), 
            settings.telegram_bot_token.encode(), 
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем hash
        if not hmac.compare_digest(calculated_hash, received_hash):
            logger.warning("Invalid hash in Telegram init_data")
            return None
        
        # Парсим данные пользователя
        user_data = {}
        if 'user' in params:
            try:
                user_info = json.loads(params['user'])
                user_data = {
                    'id': user_info.get('id'),
                    'first_name': user_info.get('first_name'),
                    'last_name': user_info.get('last_name'),
                    'username': user_info.get('username'),
                    'language_code': user_info.get('language_code'),
                    'is_premium': user_info.get('is_premium', False)
                }
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing user data: {e}")
                return None
        
        logger.info(f"Telegram user validated: {user_data.get('id')}")
        return user_data
        
    except Exception as e:
        logger.error(f"Error validating Telegram init_data: {e}")
        return None

def create_telegram_auth_middleware():
    """Создать middleware для аутентификации Telegram"""
    
    async def telegram_auth_middleware(request, call_next):
        """Middleware для проверки аутентификации Telegram"""
        
        # Пропускаем публичные маршруты
        public_paths = ['/docs', '/openapi.json', '/webhook/', '/health']
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Получаем данные инициализации из заголовков
        init_data = request.headers.get('X-Telegram-Init-Data')
        if not init_data:
            # Пытаемся получить из параметров запроса (для тестирования)
            init_data = request.query_params.get('init_data')
        
        if init_data:
            user_data = validate_telegram_init_data(init_data)
            if user_data:
                # Добавляем данные пользователя в request
                request.state.telegram_user = user_data
                return await call_next(request)
        
        # Для разработки можем пропустить проверку
        if settings.debug:
            # Создаем тестового пользователя
            request.state.telegram_user = {
                'id': 'sample_user',
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser'
            }
            return await call_next(request)
        
        # Возвращаем ошибку аутентификации
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return telegram_auth_middleware

def get_current_telegram_user(request) -> Optional[Dict[str, Any]]:
    """Получить текущего пользователя Telegram из request"""
    return getattr(request.state, 'telegram_user', None)

def format_telegram_name(user_data: Dict[str, Any]) -> str:
    """Форматировать имя пользователя Telegram"""
    first_name = user_data.get('first_name', '')
    last_name = user_data.get('last_name', '')
    username = user_data.get('username', '')
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif username:
        return f"@{username}"
    else:
        return "Unknown User"

def is_telegram_premium(user_data: Dict[str, Any]) -> bool:
    """Проверить, является ли пользователь Telegram Premium"""
    return user_data.get('is_premium', False)

def create_webapp_url(path: str = "", start_param: str = "") -> str:
    """Создать URL для Telegram WebApp"""
    base_url = settings.webapp_url.rstrip('/')
    if path:
        path = path.lstrip('/')
        base_url = f"{base_url}/{path}"
    
    if start_param:
        base_url = f"{base_url}?start_param={start_param}"
    
    return base_url

def create_telegram_bot_url(start_param: str = "") -> str:
    """Создать URL для Telegram бота"""
    bot_token = settings.telegram_bot_token
    if not bot_token:
        return ""
    
    # Извлекаем имя бота из токена
    bot_name = bot_token.split(':')[0] if ':' in bot_token else ""
    
    url = f"https://t.me/{bot_name}"
    if start_param:
        url = f"{url}?start={start_param}"
    
    return url

def validate_telegram_callback_query(callback_data: str) -> bool:
    """Валидировать callback query от Telegram"""
    try:
        # Простая валидация длины и формата
        if not callback_data or len(callback_data) > 64:
            return False
        
        # Проверяем, что содержит только допустимые символы
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-:")
        if not all(c in allowed_chars for c in callback_data):
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating callback query: {e}")
        return False