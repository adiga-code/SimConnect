# Frontend Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Копирование package.json и package-lock.json (если есть)
COPY package*.json ./

# Установка зависимостей (без --only=production для dev deps нужных для сборки)
RUN npm ci

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Production стадия
FROM nginx:alpine

# Копирование собранного приложения
COPY --from=build /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Порт
EXPOSE 3000

# Команда запуска
CMD ["nginx", "-g", "daemon off;"]