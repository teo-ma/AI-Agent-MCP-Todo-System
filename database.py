import psycopg2
import psycopg2.extras
from typing import List, Optional
from models import Todo, TodoCreate, TodoUpdate
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        
    def get_connection(self):
        return psycopg2.connect(self.connection_string)
    
    def create_todo(self, todo: TodoCreate) -> Todo:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO todos (title, content, due_date) 
                    VALUES (%s, %s, %s) 
                    RETURNING *
                    """,
                    (todo.title, todo.content, todo.due_date)
                )
                result = cursor.fetchone()
                return Todo(**result)
    
    def get_todos(self, completed: Optional[bool] = None) -> List[Todo]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                if completed is not None:
                    cursor.execute(
                        "SELECT * FROM todos WHERE completed = %s ORDER BY created_at DESC",
                        (completed,)
                    )
                else:
                    cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
                
                results = cursor.fetchall()
                return [Todo(**row) for row in results]
    
    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM todos WHERE id = %s", (todo_id,))
                result = cursor.fetchone()
                return Todo(**result) if result else None
    
    def update_todo(self, todo_id: int, todo_update: TodoUpdate) -> Optional[Todo]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # 构建动态更新查询
                update_fields = []
                values = []
                
                if todo_update.title is not None:
                    update_fields.append("title = %s")
                    values.append(todo_update.title)
                
                if todo_update.content is not None:
                    update_fields.append("content = %s")
                    values.append(todo_update.content)
                
                if todo_update.due_date is not None:
                    update_fields.append("due_date = %s")
                    values.append(todo_update.due_date)
                
                if todo_update.completed is not None:
                    update_fields.append("completed = %s")
                    values.append(todo_update.completed)
                
                if not update_fields:
                    return self.get_todo_by_id(todo_id)
                
                values.append(todo_id)
                query = f"UPDATE todos SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                return Todo(**result) if result else None
    
    def delete_todo(self, todo_id: int) -> bool:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
                return cursor.rowcount > 0
    
    def search_todos(self, query: str) -> List[Todo]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT * FROM todos 
                    WHERE title ILIKE %s OR content ILIKE %s 
                    ORDER BY created_at DESC
                    """,
                    (f"%{query}%", f"%{query}%")
                )
                results = cursor.fetchall()
                return [Todo(**row) for row in results]
