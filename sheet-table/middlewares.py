import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import Config

class AccessControlMiddleware(BaseMiddleware):
    """Middleware для контроля доступа пользователей"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        
        if user_id not in Config.ALLOWED_USER_IDS:
            self.logger.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
            
            if isinstance(event, Message):
                await event.answer(f"⛔ Доступ запрещен. Ваш ID: {user_id}")
            elif isinstance(event, CallbackQuery):
                await event.answer(f"⛔ Доступ запрещен. Ваш ID: {user_id}", show_alert=True)
            
            return
        
        self.logger.info(f"Авторизованный пользователь {user_id} выполняет действие")
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для защиты от частых запросов"""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.user_last_request = {}
        self.logger = logging.getLogger(__name__)
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        import time
        
        user_id = event.from_user.id
        current_time = time.time()
        
        if user_id in self.user_last_request:
            time_passed = current_time - self.user_last_request[user_id]
            if time_passed < self.rate_limit:
                self.logger.warning(f"Rate limit для пользователя {user_id}")
                if isinstance(event, Message):
                    await event.answer("⏱️ Слишком частые запросы. Подождите немного.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⏱️ Слишком частые запросы. Подождите немного.", show_alert=True)
                return
        
        self.user_last_request[user_id] = current_time
        return await handler(event, data)
