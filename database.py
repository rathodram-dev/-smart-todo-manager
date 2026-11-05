
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).parent / "tasks.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Medium',
                due_date TEXT DEFAULT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def get_all_tasks(search="", status="all"):
    with get_connection() as connection:
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if status == "pending":
            query += " AND completed = 0"
        elif status == "completed":
            query += " AND completed = 1"

        query += """
            ORDER BY
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            id DESC
        """

        return connection.execute(query, params).fetchall()


def add_task(title, description, priority, due_date):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO tasks
            (title, description, priority, due_date)
            VALUES (?, ?, ?, ?)
        """, (title, description, priority, due_date or None))


def get_task(task_id):
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()


def update_task(task_id, title, description, priority, due_date):
    with get_connection() as connection:
        connection.execute("""
            UPDATE tasks
            SET title = ?, description = ?,
                priority = ?, due_date = ?
            WHERE id = ?
        """, (title, description, priority, due_date or None, task_id))


def toggle_task(task_id):
    with get_connection() as connection:
        connection.execute("""
            UPDATE tasks
            SET completed = CASE
                WHEN completed = 0 THEN 1
                ELSE 0
            END
            WHERE id = ?
        """, (task_id,))


def delete_task(task_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )


def get_statistics():
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        completed = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE completed = 1"
        ).fetchone()[0]

        pending = total - completed

        percentage = round(
            completed / total * 100
        ) if total else 0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "percentage": percentage
        }
