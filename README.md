# OnlineSim - SMS Verification Service

Сервис для покупки временных номеров телефонов для SMS верификации в Telegram WebApp.

## 🚀 Возможности

- **Telegram WebApp** интеграция
- **Временные номера** из разных стран
- **SMS коды** в real-time через Server-Sent Events
- **Автоматический возврат** средств при неполучении SMS
- **Админ панель** для управления
- **Модульная архитектура** SMS провайдеров

## 🏗️ Архитектура

```
├── frontend/          # React + TypeScript + Vite
├── backend/           # FastAPI + SQLAlchemy + SQLite  
├── telegram-bot/      # aiogram Telegram Bot
├── nginx/             # Reverse Proxy
├── shared/            # Общие типы и схемы
└── docker-compose.yml # Оркестрация контейнеров
```

## 🛠️ Технологии

### Frontend
- **React 18** + TypeScript
- **Vite** (сборщик)
- **Tailwind CSS** + shadcn/ui
- **TanStack Query** (состояние сервера)
- **Wouter** (роутинг)
- **Server-Sent Events** (real-time)

### Backend
- **FastAPI** + Python 3.11
- **SQLAlchemy** + SQLite
- **Pydantic** (валидация)
- **asyncio** (асинхронность)
- **Server-Sent Events** (SSE)

### DevOps
- **Docker** + Docker Compose
- **Nginx** (reverse proxy + SSL)
- **GitHub Actions** (CI/CD, опционально)

## 🚀 Быстрый запуск

### 1. Клонирование и настройка

```bash
git clone <repository>
cd onlinesim
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте `.env`:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here
WEBAPP_URL=https://yourdomain.com

# SMS Service (опционально для продакшена)
SMS_PROVIDER=dummy
SMS_API_KEY=your-sms-api-key
SMS_WEBHOOK_SECRET=webhook-secret-key

# Security
SECRET_KEY=your-secret-key-here

# Other settings
DEBUG=False
ORDER_TIMEOUT_MINUTES=15
```

### 3. Получение токена Telegram бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в `.env`
5. Настройте Web App:
   ```
   /setmenubutton
   @your_bot_name
   OnlineSim
   https://yourdomain.com
   ```

### 4. Запуск всех сервисов

```bash
# Разработка
docker-compose up --build

# Продакшен
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 5. Проверка

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/docs
- **Health Check**: http://localhost/health

## 📁 Структура проекта

```
project-root/
├── frontend/                 # React приложение
│   ├── src/
│   │   ├── components/      # React компоненты  
│   │   ├── pages/          # Страницы приложения
│   │   ├── lib/            # Утилиты и хуки
│   │   └── main.tsx        # Точка входа
│   ├── Dockerfile
│   └── package.json
├── backend/                  # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API роуты
│   │   ├── core/           # Конфигурация и БД
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес-логика
│   │   │   └── sms/        # SMS провайдеры
│   │   └── main.py         # FastAPI приложение
│   ├── Dockerfile
│   └── requirements.txt
├── telegram-bot/            # Telegram бот
│   ├── bot.py              # Основной файл бота
│   ├── Dockerfile  
│   └── requirements.txt
├── nginx/                   # Nginx конфигурация
│   └── nginx.conf
├── docker-compose.yml       # Docker оркестрация
└── .env.example            # Пример переменных окружения
```

## 🔧 Настройка SMS провайдеров

### Добавление нового провайдера

1. Создайте файл `backend/app/services/sms/providers/your_provider.py`:

```python
from ..adapter import SMSAdapter, SMSProviderFactory

class YourProvider(SMSAdapter):
    async def order_number(self, country_code: str, service_code: str):
        # Ваша реализация
        pass
    
    async def get_sms(self, external_order_id: str):
        # Ваша реализация
        pass

# Регистрируем провайдера
SMSProviderFactory.register_provider("your_provider", YourProvider)
```

2. Обновите настройки:
```bash
SMS_PROVIDER=your_provider
SMS_API_KEY=your-api-key
```

### Настройка вебхуков

Провайдеры SMS должны отправлять POST запросы на:
```
https://yourdomain.com/api/webhook/sms/{provider_name}
```

Формат данных:
```json
{
  "order_id": "external_order_id",
  "phone_number": "+1234567890", 
  "message_text": "Your code: 12345",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🚀 Деплой на сервер

### 1. Подготовка сервера

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонирование проекта

```bash
cd /opt
sudo git clone <your-repository> onlinesim
cd onlinesim
sudo chown -R $USER:$USER .
```

### 3. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

**Обязательно измените:**
- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `SECRET_KEY` - уникальный секретный ключ
- `WEBAPP_URL` - URL вашего домена
- `SMS_API_KEY` - ключ SMS сервиса

### 4. Настройка домена и SSL

В `nginx/nginx.conf`:
```nginx
server_name yourdomain.com;

# Uncomment for SSL:
# listen 443 ssl http2;
# ssl_certificate /etc/ssl/certs/yourdomain.crt;
# ssl_certificate_key /etc/ssl/private/yourdomain.key;
```

### 5. Запуск

```bash
# Первый запуск
docker-compose up --build -d

# Проверка логов
docker-compose logs -f

# Перезапуск после изменений
git pull
docker-compose up --build -d
```

### 6. Настройка Telegram бота

После запуска настройте Web App кнопку:
```
/setmenubutton
@your_bot_name  
OnlineSim
https://yourdomain.com
```

## 🔒 Безопасность

### Обязательные настройки для продакшена:

1. **Смените секретные ключи**:
   ```bash
   SECRET_KEY=generate-strong-random-key-here
   SMS_WEBHOOK_SECRET=another-random-key
   ```

2. **Настройте SSL сертификаты** в nginx
3. **Ограничьте доступы** к базе данных
4. **Настройте backup** базы данных
5. **Мониторинг логов**

### Рекомендуемые улучшения:

- **Redis** для кэширования
- **PostgreSQL** вместо SQLite
- **Sentry** для мониторинга ошибок
- **Prometheus + Grafana** для метрик

## 📊 Мониторинг

### Доступные эндпоинты для мониторинга:

- `GET /health` - статус всех сервисов
- `GET /api/health` - статус API
- `GET /api/sse/status` - статус SSE соединений

### Логи:

```bash
# Все логи
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f telegram_bot
```

## 🔧 Разработка

### Локальная разработка:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm install
npm run dev

# Telegram Bot
cd telegram-bot
python bot.py
```

### Тестирование:

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты  
cd frontend
npm test
```

## 📝 API Документация

После запуска доступна по адресу: `http://localhost/docs`

### Основные эндпоинты:

- `GET /api/countries` - список стран
- `GET /api/services` - список сервисов  
- `POST /api/orders` - создание заказа
- `GET /api/orders` - заказы пользователя
- `GET /api/messages` - SMS сообщения
- `GET /api/events` - SSE поток событий

## ❓ FAQ

**Q: SMS не приходит, что делать?**
A: Дождитесь 15 минут - деньги вернутся автоматически. Проверьте логи SMS провайдера.

**Q: Как сменить SMS провайдера?**
A: Измените `SMS_PROVIDER` в `.env` и перезапустите контейнеры.

**Q: Как добавить новую страну?**  
A: Добавьте запись в БД через админ панель или напрямую в код инициализации.

**Q: Проблемы с Telegram WebApp?**
A: Проверьте настройки бота и URL в переменных окружения.

## 📞 Поддержка

- **Issues**: создавайте GitHub Issues
- **Документация**: обновляется в этом README
- **Мониторинг**: логи в `docker-compose logs`

## 📄 Лицензия

MIT License - свободное использование и модификация.