import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Достаем токен и записываем в переменную
BOT_TOKEN = os.getenv("BOT_TOKEN")

# На всякий случай проверяем, что токен нашелся
if not BOT_TOKEN:
    exit("Ошибка: Токен бота не найден в файле .env")
