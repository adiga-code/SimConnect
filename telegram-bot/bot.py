import asyncio
import logging
import os
from typing import Any, Dict

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, 
    WebAppInfo, MenuButtonWebApp
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:3000")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

class BotStates(StatesGroup):
    """Состояния бота"""
    waiting_for_command = State()

def create_main_keyboard() -> InlineKeyboardMarkup:
    """Создать главную клавиатуру с WebApp"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть OnlineSim",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Информация",
                    callback_data="info"
                ),
                InlineKeyboardButton(
                    text="💬 Поддержка",
                    callback_data="support"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Канал с новостями",
                    url="https://t.me/onlinesim_channel"
                )
            ]
        ]
    )
    return keyboard

def create_info_keyboard() -> InlineKeyboardMarkup:
    """Создать клавиатуру информации"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Как получить номер?",
                    callback_data="how_to_use"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Цены",
                    callback_data="prices"
                ),
                InlineKeyboardButton(
                    text="🌍 Страны", 
                    callback_data="countries"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_main"
                )
            ]
        ]
    )
    return keyboard

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start"""
    user = message.from_user
    
    # Получаем start параметр
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    logger.info(f"User {user.id} (@{user.username}) started bot with param: {start_param}")
    
    welcome_text = f"""
🎉 <b>Добро пожаловать в OnlineSim!</b>

Привет, <b>{user.first_name}</b>! 

Я помогу вам получить временные номера телефонов для регистрации в различных сервисах:

📱 <b>Telegram, WhatsApp, Discord</b> и многие другие
🌍 Номера из <b>России, Украины, Казахстана</b> и других стран
⚡ <b>Быстро</b> и <b>надежно</b>
💰 Низкие цены от <b>15₽</b>

Нажмите кнопку ниже, чтобы начать пользоваться сервисом!
    """
    
    await message.answer(
        welcome_text,
        reply_markup=create_main_keyboard()
    )
    
    # Устанавливаем кнопку меню WebApp
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(
            text="OnlineSim",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )

@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Обработчик команды /help"""
    help_text = """
🆘 <b>Помощь по использованию OnlineSim</b>

<b>Доступные команды:</b>
/start - Главное меню
/help - Эта справка
/support - Техподдержка

<b>Как использовать:</b>
1️⃣ Нажмите кнопку "Открыть OnlineSim"
2️⃣ Выберите страну и сервис
3️⃣ Оплатите заказ
4️⃣ Получите номер и ждите SMS
5️⃣ Используйте полученный код

<b>Время ожидания SMS:</b> до 15 минут
<b>При неполучении:</b> деньги автоматически возвращаются

Нужна помощь? Обращайтесь в поддержку! 👇
    """
    
    await message.answer(
        help_text,
        reply_markup=create_main_keyboard()
    )

@router.message(Command("support"))
async def support_handler(message: Message) -> None:
    """Обработчик команды /support"""
    support_text = """
💬 <b>Техническая поддержка</b>

Если у вас возникли вопросы или проблемы, мы поможем!

<b>Способы связи:</b>
• Telegram: @support
• Email: support@onlinesim.com

<b>Время работы:</b> 24/7

<b>Частые вопросы:</b>
• SMS не приходит - ждите до 15 минут, деньги вернутся автоматически
• Проблемы с оплатой - проверьте баланс аккаунта
• Нет нужной страны - следите за обновлениями в канале

Мы отвечаем в течение нескольких минут! ⚡
    """
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать в поддержку",
                    url="https://t.me/support"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_main"
                )
            ]
        ]
    )
    
    await message.answer(support_text, reply_markup=keyboard)

@router.callback_query(F.data == "info")
async def info_callback(callback_query) -> None:
    """Обработчик кнопки "Информация"""
    info_text = """
ℹ️ <b>Информация об OnlineSim</b>

<b>Что мы предлагаем:</b>
🔹 Временные номера для SMS верификации
🔹 Поддержка популярных сервисов
🔹 Номера из разных стран мира
🔹 Быстрая доставка SMS кодов

<b>Преимущества:</b>
✅ Низкие цены
✅ Высокая скорость получения SMS
✅ Автоматический возврат средств
✅ Круглосуточная поддержка
✅ Простой интерфейс

Выберите интересующую информацию:
    """
    
    await callback_query.message.edit_text(
        info_text,
        reply_markup=create_info_keyboard()
    )
    await callback_query.answer()

@router.callback_query(F.data == "how_to_use")
async def how_to_use_callback(callback_query) -> None:
    """Обработчик кнопки "Как получить номер?"""
    instruction_text = """
📱 <b>Пошаговая инструкция</b>

<b>1️⃣ Откройте приложение</b>
Нажмите кнопку "Открыть OnlineSim"

<b>2️⃣ Выберите сервис</b>
Telegram, WhatsApp, Discord или другой

<b>3️⃣ Выберите страну</b>
Россия, Украина, Казахстан и др.

<b>4️⃣ Пополните баланс</b>
Если средств недостаточно

<b>5️⃣ Заказать номер</b>
Нажмите кнопку "Купить номер"

<b>6️⃣ Получите номер</b>
Номер появится в разделе "Номера"

<b>7️⃣ Ждите SMS</b>
До 15 минут, код появится автоматически

<b>8️⃣ Используйте код</b>
Скопируйте и вставьте в нужный сервис

❗ <b>Важно:</b> Если SMS не пришло в течение 15 минут, деньги автоматически вернутся на баланс.
    """
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Попробовать сейчас",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="info"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        instruction_text,
        reply_markup=keyboard
    )
    await callback_query.answer()

@router.callback_query(F.data == "prices")
async def prices_callback(callback_query) -> None:
    """Обработчик кнопки "Цены"""
    prices_text = """
💰 <b>Цены на номера</b>

<b>🇷🇺 Россия</b>
• Telegram: от 15₽
• WhatsApp: от 18₽
• Discord: от 20₽

<b>🇺🇦 Украина</b>
• Telegram: от 22₽
• WhatsApp: от 25₽
• Discord: от 28₽

<b>🇰🇿 Казахстан</b>
• Telegram: от 18₽
• WhatsApp: от 20₽
• Discord: от 25₽

<b>🇺🇸 США</b>
• Telegram: от 45₽
• WhatsApp: от 50₽
• Discord: от 55₽

💡 <b>Скидки:</b>
• При пополнении от 500₽ - скидка 5%
• Постоянным клиентам - до 10%

Актуальные цены смотрите в приложении!
    """
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Пополнить баланс",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?tab=profile")
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="info"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        prices_text,
        reply_markup=keyboard
    )
    await callback_query.answer()

@router.callback_query(F.data == "countries")
async def countries_callback(callback_query) -> None:
    """Обработчик кнопки "Страны"""
    countries_text = """
🌍 <b>Доступные страны</b>

<b>🟢 Активные (много номеров):</b>
🇷🇺 Россия - 1200+ номеров
🇺🇦 Украина - 850+ номеров

<b>🟡 Ограниченно (мало номеров):</b>
🇰🇿 Казахстан - 15+ номеров

<b>🔴 Недоступные:</b>
🇺🇸 США - временно нет номеров

<b>🔄 Скоро добавим:</b>
🇧🇾 Беларусь
🇵🇱 Польша
🇩🇪 Германия

Следите за обновлениями в нашем канале!
    """
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Канал с обновлениями",
                    url="https://t.me/onlinesim_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="info"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        countries_text,
        reply_markup=keyboard
    )
    await callback_query.answer()

@router.callback_query(F.data == "support")
async def support_callback(callback_query) -> None:
    """Обработчик кнопки "Поддержка"""
    await support_handler(callback_query.message)
    await callback_query.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback_query) -> None:
    """Обработчик кнопки "Назад в главное меню"""
    welcome_text = """
🎉 <b>OnlineSim - Временные номера телефонов</b>

📱 <b>Получайте SMS коды быстро и надежно!</b>

🌟 Поддерживаемые сервисы:
• Telegram, WhatsApp, Discord
• Instagram, Twitter, VKontakte
• И многие другие...

💰 Цены от 15₽ | ⚡ SMS за 1-5 минут | 🔄 Автовозврат средств

Нажмите кнопку ниже, чтобы начать!
    """
    
    await callback_query.message.edit_text(
        welcome_text,
        reply_markup=create_main_keyboard()
    )
    await callback_query.answer()

# Обработчик всех остальных сообщений
@router.message()
async def echo_handler(message: Message) -> None:
    """Обработчик остальных сообщений"""
    await message.answer(
        "Используйте команды /start или /help для получения информации.",
        reply_markup=create_main_keyboard()
    )

# Регистрируем роутер
dp.include_router(router)

async def main() -> None:
    """Главная функция запуска бота"""
    logger.info("Starting OnlineSim Telegram Bot...")
    
    # Удаляем webhook если есть
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())