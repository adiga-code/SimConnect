import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ...schemas.schemas import SMSWebhookData, Message

logger = logging.getLogger(__name__)

class SMSValidator:
    """Валидатор SMS данных - промежуточный файл для обработки данных перед отправкой во фронт"""
    
    @staticmethod
    def extract_verification_code(message_text: str) -> Optional[str]:
        """Извлечь код верификации из SMS текста"""
        if not message_text:
            return None
        
        # Различные паттерны для поиска кода
        patterns = [
            r'\b(\d{4,6})\b',  # 4-6 цифр подряд
            r'код:?\s*(\d+)',  # "код: 12345"
            r'code:?\s*(\d+)',  # "code: 12345" 
            r'verification:?\s*(\d+)',  # "verification: 12345"
            r'confirm:?\s*(\d+)',  # "confirm: 12345"
            r'your\s+code:?\s*(\d+)',  # "your code: 12345"
            r'(\d+)\s+is\s+your',  # "12345 is your code"
            r'(\d{4,6})\D',  # 4-6 цифр с не-цифрой после
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if 4 <= len(match) <= 6 and match.isdigit():
                    logger.info(f"Extracted code '{match}' from message: {message_text}")
                    return match
        
        logger.warning(f"No verification code found in message: {message_text}")
        return None
    
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        """Проверить корректность номера телефона"""
        if not phone_number:
            return False
        
        # Убираем все кроме цифр и +
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Должен начинаться с + и содержать от 10 до 15 цифр
        pattern = r'^\+\d{10,15}
        is_valid = bool(re.match(pattern, clean_number))
        
        if not is_valid:
            logger.warning(f"Invalid phone number format: {phone_number}")
        
        return is_valid
    
    @staticmethod
    def sanitize_message_text(message_text: str) -> str:
        """Очистить текст сообщения от лишних символов"""
        if not message_text:
            return ""
        
        # Убираем лишние пробелы и переносы строк
        cleaned = re.sub(r'\s+', ' ', message_text.strip())
        
        # Убираем специальные символы, которые могут сломать JSON
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def validate_webhook_data(data: Dict[str, Any]) -> Optional[SMSWebhookData]:
        """Валидировать данные вебхука от SMS сервиса"""
        try:
            # Обязательные поля
            required_fields = ['order_id', 'phone_number', 'message_text']
            for field in required_fields:
                if field not in data or not data[field]:
                    logger.error(f"Missing required field in webhook data: {field}")
                    return None
            
            # Валидация номера телефона
            if not SMSValidator.validate_phone_number(data['phone_number']):
                logger.error(f"Invalid phone number in webhook: {data['phone_number']}")
                return None
            
            # Очистка и извлечение кода
            message_text = SMSValidator.sanitize_message_text(data['message_text'])
            code = SMSValidator.extract_verification_code(message_text)
            
            # Создаем объект с валидированными данными
            webhook_data = SMSWebhookData(
                order_id=str(data['order_id']),
                phone_number=data['phone_number'],
                message_text=message_text,
                code=code,
                timestamp=data.get('timestamp', datetime.now())
            )
            
            logger.info(f"Successfully validated webhook data for order: {webhook_data.order_id}")
            return webhook_data
            
        except Exception as e:
            logger.error(f"Error validating webhook data: {e}")
            return None
    
    @staticmethod
    def prepare_frontend_message(order_id: str, message_text: str, code: Optional[str] = None) -> Dict[str, Any]:
        """Подготовить данные сообщения для отправки во фронтенд"""
        
        # Если код не передан, попытаемся извлечь
        if not code:
            code = SMSValidator.extract_verification_code(message_text)
        
        # Очищаем текст
        clean_text = SMSValidator.sanitize_message_text(message_text)
        
        frontend_data = {
            "order_id": order_id,
            "message_text": clean_text,
            "code": code,
            "has_code": bool(code),
            "received_at": datetime.now().isoformat(),
            "status": "received"
        }
        
        logger.info(f"Prepared frontend message for order {order_id}: code={'found' if code else 'not found'}")
        return frontend_data
    
    @staticmethod
    def validate_order_status_transition(current_status: str, new_status: str) -> bool:
        """Проверить корректность перехода статуса заказа"""
        
        valid_transitions = {
            "pending": ["received", "expired", "cancelled"],
            "received": [],  # Финальный статус
            "expired": [],   # Финальный статус
            "cancelled": []  # Финальный статус
        }
        
        if current_status not in valid_transitions:
            logger.error(f"Invalid current status: {current_status}")
            return False
        
        if new_status not in valid_transitions[current_status]:
            logger.warning(f"Invalid status transition: {current_status} -> {new_status}")
            return False
        
        return True
    
    @staticmethod
    def is_message_duplicate(existing_messages: list, new_message_text: str) -> bool:
        """Проверить, является ли сообщение дубликатом"""
        if not existing_messages or not new_message_text:
            return False
        
        clean_new = SMSValidator.sanitize_message_text(new_message_text)
        
        for msg in existing_messages:
            if hasattr(msg, 'text'):
                existing_text = SMSValidator.sanitize_message_text(msg.text)
                if existing_text == clean_new:
                    logger.warning(f"Duplicate message detected: {clean_new}")
                    return True
        
        return False