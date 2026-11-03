import os
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

DB_PATH = os.environ.get("INVENTORY_DB", "inventory.db")

app = FastAPI(title="Inventory API")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS items (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               category TEXT NOT NULL,
               price TEXT NOT NULL
           )"""
    )
    try:
        yield conn
    finally:
        conn.close()


class ItemIn(BaseModel):
    name: str
    category: str
    price: float


@app.post("/items", status_code=201)
def create_item(item: ItemIn, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute(
        "INSERT INTO items (name, category, price) VALUES (?, ?, ?)",
        (item.name, item.category, str(item.price)),
    )
    db.commit()
    return {"id": cur.lastrowid, **item.model_dump()}


@app.get("/items/{item_id}")
def get_item(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(row)


@app.get("/items")
def list_items(
    category: str | None = None,
    min_price: str | None = None,
    max_price: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: sqlite3.Connection = Depends(get_db),
):
    """List items. min_price and max_price are inclusive bounds."""
    clauses, params = [], []
    if category:
        clauses.append("category = ?")
        params.append(category)
    if min_price is not None:
        clauses.append("price > ?")
        params.append(min_price)
    if max_price is not None:
        clauses.append("price <= ?")
        params.append(max_price)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    offset = (page - 1) * page_size + (1 if page > 1 else 0)

    rows = db.execute(
        f"SELECT * FROM items {where} ORDER BY id LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return {"page": page, "page_size": page_size, "items": [dict(r) for r in rows]}