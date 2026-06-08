import aiosqlite

DB_PATH = "todo_bot.db"

async def db_start():
    # Асинхронно подключаемся к базе (если файла нет, он создастся)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            )
        """)
        # Создаем таблицу для задач, если она еще не создана
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_text TEXT NOT NULL
            )
        """)
        # Сохраняем изменения
        await db.commit()
    print("База данных успешно подключена и проверена!")
async def add_user_to_db(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        # INSERT OR IGNORE просто пропустит запись, если такой user_id уже есть в базе
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def add_task_to_db(user_id: int, task_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        # Знак вопроса (?) защищает от SQL-инъекций
        await db.execute(
            "INSERT INTO tasks (user_id, task_text) VALUES (?, ?)",
            (user_id, task_text)
        )
        await db.commit()

async def get_all_users() -> list:
    """Возвращает список всех зарегистрированных пользователей"""
    async with aiosqlite.connect(DB_PATH) as db:
        # fetchall() возвращает список кортежей, например: [(12345, 'ivan'), (67890, 'pavel')]
        async with db.execute("SELECT user_id, username FROM users") as cursor:
            return await cursor.fetchall()


async def get_user_tasks(user_id: int) -> list:
    """Возвращает список задач для конкретного пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Выбираем id задачи и её текст для конкретного user_id
        async with db.execute(
            "SELECT id, task_text FROM tasks WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()

async def delete_task_from_db(task_id: int):
    """Удаляет задачу по её уникальному ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()
