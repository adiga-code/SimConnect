from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging
from contextlib import asynccontextmanager

from .core.config import settings
from .api.routes import router
from .services.sms.adapter import SMSAdapter

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для SMS адаптера
sms_adapter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global sms_adapter
    
    # Startup
    try:
        logger.info("Initializing SMS adapter...")
        sms_adapter = SMSAdapter(
            provider_name=getattr(settings, 'SMS_PROVIDER', 'dummy'),
            api_key=getattr(settings, 'SMS_API_KEY', None)
        )
        logger.info("SMS adapter initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SMS adapter: {e}")
        # Используем dummy provider как fallback
        sms_adapter = SMSAdapter(provider_name="dummy")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

# Создание FastAPI приложения
app = FastAPI(
    title="OnlineSim API",
    description="API для получения SMS на виртуальные номера",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В Codespaces разрешаем все origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов API
app.include_router(router, prefix="/api")

# Статические файлы (фронтенд)
if os.path.exists("/app/frontend/dist"):
    app.mount("/static", StaticFiles(directory="/app/frontend/dist"), name="static")
    
    @app.get("/")
    async def read_root():
        """Главная страница - возвращаем index.html фронтенда"""
        return FileResponse("/app/frontend/dist/index.html")
    
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """Перенаправляем все остальные запросы на index.html для SPA"""
        # Проверяем, не запрос ли это к API
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        
        # Проверяем, существует ли файл
        file_path = f"/app/frontend/dist/{full_path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Для всех остальных запросов возвращаем index.html
        return FileResponse("/app/frontend/dist/index.html")

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "ok",
        "sms_provider": settings.SMS_PROVIDER if sms_adapter else "not initialized"
    }

def get_sms_adapter() -> SMSAdapter:
    """Получить экземпляр SMS адаптера"""
    global sms_adapter
    if sms_adapter is None:
        # Создаем fallback адаптер если основной не инициализирован
        sms_adapter = SMSAdapter(provider_name="dummy")
    return sms_adapter