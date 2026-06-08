from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    # Создаем строитель клавиатур
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки. callback_data — это "сигнал", который прилетит боту при нажатии
    builder.button(text="➕ Добавить задачу", callback_data="add_task")
    builder.button(text="📋 Мои задачи", callback_data="my_tasks")

    # Размещаем кнопки друг под другом (в 1 столбец)
    builder.adjust(1)

    # Возвращаем готовую клавиатуру
    return builder.as_markup()

def get_tasks_keyboard(tasks_list: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # tasks_list будет приходить из базы в виде: [(id, text), (id, text)...]
    for task_id, task_text in tasks_list:
        # Для каждой задачи создаем кнопку удаления.
        # В callback_data записываем строку вида "delete_1", "delete_5" и т.д.
        short_text = task_text if len(task_text) <= 15 else f"{task_text[:15]}..."
        builder.button(text=f"❌ Удалить: {short_text}", callback_data=f"delete_{task_id}")

    # В самом конце добавляем кнопку возврата в главное меню
    builder.button(text="🔙 Назад в меню", callback_data="main_menu")

    # Размещаем все кнопки в один столбец
    builder.adjust(1)
    return builder.as_markup()
