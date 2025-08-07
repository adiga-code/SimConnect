# Frontend Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production=false

# Копирование конфигурационных файлов
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.ts ./
COPY postcss.config.js ./
COPY components.json ./
COPY drizzle.config.ts ./

# Переменные окружения для продакшена
RUN echo "VITE_API_URL=https://app2.hezh-digital.ru/api" > .env && \
    echo "VITE_SSE_URL=https://app2.hezh-digital.ru/api/events" >> .env && \
    echo "VITE_WEBAPP_URL=https://app2.hezh-digital.ru" >> .env

# Копирование исходного кода
COPY src/ ./src/
COPY index.html ./

# Копирование shared папки (находится на уровень выше)
COPY ../shared/ ./shared/

# Сборка приложения
RUN npm run build

# Production стадия
FROM nginx:alpine

# Удаление дефолтной конфигурации nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копирование собранного приложения
COPY --from=build /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Порт
EXPOSE 3000

# Команда запуска
CMD ["nginx", "-g", "daemon off;"]