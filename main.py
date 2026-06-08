import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database.db import db_start

from handlers import common # Импортируем наши будущие хэндлеры
from handlers import tasks

# Включаем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализируем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await db_start()
    # Регистрируем роутеры (подключаем логику из других файлов)
    dp.include_router(common.router)
    dp.include_router(tasks.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
