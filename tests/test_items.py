import os
import tempfile

import pytest
from fastapi.testclient import TestClient

os.environ["INVENTORY_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    import sqlite3

    conn = sqlite3.connect(os.environ["INVENTORY_DB"])
    conn.execute("DROP TABLE IF EXISTS items")
    conn.commit()
    conn.close()


def add(name, category, price):
    return client.post("/items", json={"name": name, "category": category, "price": price})


def test_create_and_get_item():
    r = add("Pen", "office", 3)
    assert r.status_code == 201
    item_id = r.json()["id"]
    assert client.get(f"/items/{item_id}").json()["name"] == "Pen"


def test_missing_item_returns_404():
    assert client.get("/items/999").status_code == 404


def test_filter_by_category():
    add("Pen", "office", 3)
    add("Mouse", "tech", 5)
    names = [i["name"] for i in client.get("/items?category=tech").json()["items"]]
    assert names == ["Mouse"]


def test_filter_by_price_range():
    add("A", "office", 2)
    add("B", "office", 5)
    add("C", "office", 8)
    names = [i["name"] for i in client.get("/items?min_price=3&max_price=9").json()["items"]]
    assert names == ["B", "C"]


def test_list_items_single_page():
    for n in range(4):
        add(f"Item{n}", "office", n + 1)
    assert len(client.get("/items").json()["items"]) == 4