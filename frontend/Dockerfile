# Frontend Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production=false

# Копирование конфигурационных файлов
COPY vite.config.js ./
COPY .env.production ./.env

# Копирование исходного кода
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./

# Копирование shared папки если есть
COPY ../shared/ ./shared/ 2>/dev/null || true
COPY ../attached_assets/ ./attached_assets/ 2>/dev/null || true

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