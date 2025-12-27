from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
import string
import random

app = FastAPI(title="Short URL Service")

DB_PATH = "/app/data/shorturl.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                short_id TEXT PRIMARY KEY,
                full_url TEXT NOT NULL
            )
        """)


@app.on_event("startup")
def startup():
    init_db()


def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


class URLCreate(BaseModel):
    url: str


@app.post("/shorten")
def shorten_url(data: URLCreate):
    short_id = generate_short_id()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO urls (short_id, full_url) VALUES (?, ?)",
            (short_id, data.url)
        )
    return {"short_url": f"/{short_id}", "short_id": short_id}


@app.get("/{short_id}")
def redirect(short_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT full_url FROM urls WHERE short_id=?",
            (short_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=row[0])


@app.get("/stats/{short_id}")
def stats(short_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT short_id, full_url FROM urls WHERE short_id=?",
            (short_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"short_id": row[0], "full_url": row[1]}
