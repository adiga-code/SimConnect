import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import Request
from fastapi.responses import StreamingResponse
from ..schemas.schemas import SSEEvent

logger = logging.getLogger(__name__)

class SSEManager:
    """Менеджер для Server-Sent Events"""
    
    def __init__(self):
        self.connections: Dict[str, List[asyncio.Queue]] = {}
    
    async def connect(self, user_id: str) -> asyncio.Queue:
        """Подключить пользователя к SSE"""
        queue = asyncio.Queue()
        
        if user_id not in self.connections:
            self.connections[user_id] = []
        
        self.connections[user_id].append(queue)
        logger.info(f"SSE connection added for user {user_id}")
        
        return queue
    
    async def disconnect(self, user_id: str, queue: asyncio.Queue):
        """Отключить пользователя от SSE"""
        if user_id in self.connections:
            try:
                self.connections[user_id].remove(queue)
                if not self.connections[user_id]:
                    del self.connections[user_id]
                logger.info(f"SSE connection removed for user {user_id}")
            except ValueError:
                pass
    
    async def send_to_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Отправить событие конкретному пользователю"""
        if user_id not in self.connections:
            logger.debug(f"No SSE connections for user {user_id}")
            return
        
        event = SSEEvent(type=event_type, data=data)
        message = self._format_sse_message(event)
        
        # Отправляем во все активные соединения пользователя
        disconnected_queues = []
        for queue in self.connections[user_id]:
            try:
                await queue.put(message)
            except Exception as e:
                logger.error(f"Error sending SSE message: {e}")
                disconnected_queues.append(queue)
        
        # Удаляем неактивные соединения
        for queue in disconnected_queues:
            await self.disconnect(user_id, queue)
        
        logger.debug(f"SSE event sent to user {user_id}: {event_type}")
    
    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Отправить событие всем подключенным пользователям"""
        event = SSEEvent(type=event_type, data=data)
        message = self._format_sse_message(event)
        
        for user_id in list(self.connections.keys()):
            await self.send_to_user(user_id, event_type, data)
        
        logger.debug(f"SSE event broadcasted: {event_type}")
    
    def _format_sse_message(self, event: SSEEvent) -> str:
        """Форматировать сообщение в формате SSE"""
        data_json = json.dumps(event.data, ensure_ascii=False)
        return f"event: {event.type}\ndata: {data_json}\n\n"
    
    def get_connection_count(self, user_id: str) -> int:
        """Получить количество активных соединений пользователя"""
        return len(self.connections.get(user_id, []))
    
    def get_total_connections(self) -> int:
        """Получить общее количество активных соединений"""
        return sum(len(queues) for queues in self.connections.values())

# Глобальный экземпляр менеджера
sse_manager = SSEManager()

async def create_sse_stream(request: Request, user_id: str):
    """Создать поток SSE для пользователя"""
    
    async def event_stream():
        queue = await sse_manager.connect(user_id)
        
        try:
            # Отправляем приветственное сообщение
            welcome_message = sse_manager._format_sse_message(
                SSEEvent(
                    type="connected",
                    data={
                        "message": "SSE connection established",
                        "timestamp": str(asyncio.get_event_loop().time())
                    }
                )
            )
            yield welcome_message
            
            # Отправляем keep-alive каждые 30 секунд
            keep_alive_task = asyncio.create_task(send_keep_alive(queue))
            
            # Обрабатываем события
            while True:
                try:
                    # Ждем новое сообщение с таймаутом
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield message
                    
                except asyncio.TimeoutError:
                    # Проверяем, не отключился ли клиент
                    if await request.is_disconnected():
                        break
                    continue
                    
                except Exception as e:
                    logger.error(f"Error in SSE stream: {e}")
                    break
            
        except Exception as e:
            logger.error(f"Error in SSE event stream: {e}")
            
        finally:
            # Очистка при отключении
            keep_alive_task.cancel()
            await sse_manager.disconnect(user_id, queue)
    
    return event_stream()

async def send_keep_alive(queue: asyncio.Queue):
    """Отправлять keep-alive сообщения"""
    try:
        while True:
            await asyncio.sleep(30)  # Каждые 30 секунд
            
            keep_alive_message = sse_manager._format_sse_message(
                SSEEvent(
                    type="keep_alive",
                    data={"timestamp": str(asyncio.get_event_loop().time())}
                )
            )
            
            await queue.put(keep_alive_message)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error in keep-alive task: {e}")

def create_sse_response(request: Request, user_id: str) -> StreamingResponse:
    """Создать SSE response"""
    return StreamingResponse(
        create_sse_stream(request, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )