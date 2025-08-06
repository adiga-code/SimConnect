# Telegram Bot Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование бота
COPY . .

# Создание пользователя без прав root
RUN adduser --disabled-password --gecos '' botuser && chown -R botuser /app
USER botuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "bot.py"]