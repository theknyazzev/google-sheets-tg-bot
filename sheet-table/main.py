import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from google_sheets import GoogleSheetsService
from handlers import BotHandlers
from middlewares import AccessControlMiddleware, RateLimitMiddleware

# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

async def main():
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Проверка конфигурации
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в переменных окружения")
        return
    
    if not Config.GOOGLE_SHEET_ID:
        logger.error("GOOGLE_SHEET_ID не установлен в переменных окружения")
        return
    
    if not Config.ALLOWED_USER_IDS:
        logger.error("ALLOWED_USER_IDS не установлен в переменных окружения")
        return
    
    logger.info("Запуск бота...")
    logger.info(f"Разрешенные пользователи: {Config.ALLOWED_USER_IDS}")
    logger.info(f"Google Sheet ID: {Config.GOOGLE_SHEET_ID}")
    logger.info(f"Лист: {Config.WORKSHEET_NAME}")
    
    # Инициализация компонентов
    bot = Bot(token=Config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Инициализация Google Sheets
    sheets_service = GoogleSheetsService()
    sheets_init_success = await sheets_service.init_service()
    
    if not sheets_init_success:
        logger.error("Не удалось подключиться к Google Sheets. Проверьте credentials.json и настройки.")
        return
    
    # Инициализация обработчиков
    handlers = BotHandlers(sheets_service)
    
    # Подключение middleware
    dp.message.middleware(AccessControlMiddleware())
    dp.callback_query.middleware(AccessControlMiddleware())
    dp.message.middleware(RateLimitMiddleware(rate_limit=1.0))
    dp.callback_query.middleware(RateLimitMiddleware(rate_limit=0.5))
    
    # Подключение роутера
    dp.include_router(handlers.router)
    
    try:
        logger.info("Бот успешно запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")
