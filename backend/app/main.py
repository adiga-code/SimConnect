import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.database import create_tables
from .api.routes import router
from .utils.telegram import create_telegram_auth_middleware
from .services.order_service import start_cleanup_task
from .data_init import initialize_data

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    logger.info("Starting OnlineSim FastAPI application...")
    
    # Создание таблиц БД
    create_tables()
    logger.info("Database tables created")
    
    # Инициализация начальных данных
    await initialize_data()
    logger.info("Initial data loaded")
    
    # Запуск фоновых задач
    cleanup_task = asyncio.create_task(start_cleanup_task())
    logger.info("Background tasks started")
    
    yield
    
    # Завершение работы
    logger.info("Shutting down OnlineSim application...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

# Создание FastAPI приложения
app = FastAPI(
    title="OnlineSim API",
    description="API для сервиса покупки временных номеров телефонов",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Telegram Auth middleware
app.add_middleware("http", create_telegram_auth_middleware())

# Глобальный обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Подключение роутов
app.include_router(router)

# Основные endpoints
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "OnlineSim API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )