from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import add_user_to_db

from keyboards.inline import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    username=message.from_user.username or "No Username"

    keyboard = get_main_menu()

    await add_user_to_db(user_id=message.from_user.id, username=username)

    await message.answer(f"Привествую, {message.from_user.full_name}!\n Выберите действие ниже:", reply_markup=keyboard)
