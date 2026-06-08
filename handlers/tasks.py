from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_main_menu, get_tasks_keyboard
from database.db import add_task_to_db, get_user_tasks, delete_task_from_db

router = Router()

# 1. Создаем группу состояний
class TaskStates(StatesGroup):
    waiting_for_task_text = State()  # Состояние ожидания текста задачи


# 2. Ловим нажатие на кнопку "Добавить задачу"
@router.callback_query(F.data == "add_task")
async def add_task_start(callback: CallbackQuery, state: FSMContext):
    # Включаем состояние ожидания текста
    await state.set_state(TaskStates.waiting_for_task_text)

    # Отвечаем на колбэк (чтобы кнопка не "зависала" в режиме загрузки)
    await callback.answer()

    # Просим пользователя ввести текст
    await callback.message.answer("Введите текст задачи:")


# 3. Ловим текстовое сообщение, НО только когда бот в состоянии waiting_for_task_text
@router.message(TaskStates.waiting_for_task_text, F.text)
async def process_task_text(message: Message, state: FSMContext):
    task_text = message.text  # Вот он, текст нашей задачи!
    keyboard = get_main_menu()

    # TODO: Тут будет сохранение в базу данных!
    await add_task_to_db(user_id=message.from_user.id, task_text=task_text)
    # Сбрасываем состояние (выходим из режима ожидания)
    await state.clear()

    # Возвращаем пользователя в главное меню
    await message.answer(
        f"✅ Задача успешно добавлена:\n\n*«{task_text}»*",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# 1. Хэндлер для кнопки "📋 Мои задачи"
@router.callback_query(F.data == "my_tasks")
async def show_tasks(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # Достаем список задач из базы данных.
    # Каждая задача придет в виде кортежа (id, task_text)
    tasks = await get_user_tasks(user_id)

    if not tasks:
        await callback.message.answer("📭 Ваш список дел пока пуст!")
        return

    # Формируем красивый текстовый список для пользователя
    text_message = "📋 **Ваши задачи:**\n\n"
    for index, (task_id, task_text) in enumerate(tasks, start=1):
        text_message += f"{index}. {task_text}\n"

    text_message += "\nНажмите на кнопку ниже, чтобы удалить выполненную задачу:"

    # Генерируем клавиатуру, передавая туда наш список задач
    keyboard = get_tasks_keyboard(tasks)

    await callback.message.answer(
        text_message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# 2. Хэндлер удаления. Ловит ЛЮБОЙ callback_data, который начинается на "delete_"
@router.callback_query(F.data.startswith("delete_"))
async def delete_task_handler(callback: CallbackQuery):
    # callback.data выглядит как "delete_25"
    # .split("_") делит строку по знаку подчеркивания на список: ["delete", "25"]
    # [1] берет второй элемент этого списка (то есть "25"), и мы превращаем его в инт int()
    task_id = int(callback.data.split("_")[1])

    # Удаляем задачу из базы данных по её уникальному id
    await delete_task_from_db(task_id)

    # Отправляем всплывающее уведомление в Telegram (оно пропадет само через пару секунд)
    await callback.answer("✅ Задача удалена!", show_alert=False)

    # А теперь обновляем сообщение со списком задач, чтобы удаленная задача сразу исчезла!
    user_id = callback.from_user.id
    tasks = await get_user_tasks(user_id)

    if not tasks:
        # Если задач больше нет, редактируем старое сообщение на текст о пустом списке
        await callback.message.edit_text("📭 Ваш список дел теперь пуст!", reply_markup=get_main_menu())
        return

    # Если задачи еще есть, заново генерируем текст и клавиатуру
    text_message = "📋 **Ваши задачи:**\n\n"
    for index, (t_id, t_text) in enumerate(tasks, start=1):
        text_message += f"{index}. {t_text}\n"
    text_message += "\nНажмите на кнопку ниже, чтобы удалить выполненную задачу:"

    keyboard = get_tasks_keyboard(tasks)

    # Изменяем текущее сообщение (и текст, и кнопки) вместо отправки нового
    await callback.message.edit_text(text_message, parse_mode="Markdown", reply_markup=keyboard)


# 3. Хэндлер для кнопки "🔙 Назад в меню"
@router.callback_query(F.data == "main_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.answer()
    # Просто меняем текст сообщения на главное меню и возвращаем стартовую клавиатуру
    await callback.message.edit_text(
        f"Приветствую, {callback.from_user.full_name}!\nВыберите действие ниже:",
        reply_markup=get_main_menu()
    )
