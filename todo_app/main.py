from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI(title="ToDo Service")

DB_PATH = "/app/data/todo.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        """)


@app.on_event("startup")
def startup():
    init_db()


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class Todo(TodoCreate):
    id: int

class TodoPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

@app.post("/items", response_model=Todo)
def create_item(item: TodoCreate):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
            (item.title, item.description, item.completed)
        )
        item_id = cursor.lastrowid
    return Todo(id=item_id, **item.dict())


@app.get("/items", response_model=List[Todo])
def get_items():
    with get_db() as conn:
        rows = conn.execute("SELECT id, title, description, completed FROM items").fetchall()
    return [Todo(id=r[0], title=r[1], description=r[2], completed=bool(r[3])) for r in rows]


@app.get("/items/{item_id}", response_model=Todo)
def get_item(item_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, title, description, completed FROM items WHERE id=?",
            (item_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return Todo(id=row[0], title=row[1], description=row[2], completed=bool(row[3]))


@app.put("/items/{item_id}", response_model=Todo)
def update_item(item_id: int, item: TodoCreate):
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE items SET title=?, description=?, completed=? WHERE id=?",
            (item.title, item.description, item.completed, item_id)
        )
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return Todo(id=item_id, **item.dict())

@app.patch("/items/{item_id}", response_model=Todo)
def patch_item(item_id: int, item: TodoPatch):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, title, description, completed FROM items WHERE id=?",
            (item_id,)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Item not found")

        current = {
            "title": row[1],
            "description": row[2],
            "completed": bool(row[3]),
        }

        updated = {
            "title": item.title if item.title is not None else current["title"],
            "description": item.description if item.description is not None else current["description"],
            "completed": item.completed if item.completed is not None else current["completed"],
        }

        conn.execute(
            """
            UPDATE items
            SET title=?, description=?, completed=?
            WHERE id=?
            """,
            (updated["title"], updated["description"], updated["completed"], item_id)
        )

    return Todo(id=item_id, **updated)

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted"}
