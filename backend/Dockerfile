# Build stage for frontend
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ ./
COPY shared/ ../shared/

# Create production .env
RUN echo "VITE_API_URL=https://app2.hezh-digital.ru/api" > .env.production && \
    echo "VITE_SSE_URL=https://app2.hezh-digital.ru/api/events" >> .env.production && \
    echo "VITE_WEBAPP_URL=https://app2.hezh-digital.ru" >> .env.production

# Build frontend
RUN npm run build

# Build stage for backend
FROM python:3.11-slim as backend-build

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from build stage
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist/

# Copy shared files
COPY shared/ ./shared/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]