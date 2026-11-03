"""Fill the database with sample items: python seed.py"""
import sqlite3

from main import DB_PATH

ITEMS = [
    ("Pen", "office", 3), ("Notebook", "office", 7), ("Stapler", "office", 15),
    ("Desk Lamp", "office", 24), ("Monitor Stand", "office", 45),
    ("Keyboard", "tech", 60), ("Mouse", "tech", 25), ("Webcam", "tech", 80),
    ("Headset", "tech", 99), ("USB Hub", "tech", 20), ("Monitor", "tech", 150),
    ("Laptop Stand", "tech", 100), ("SSD 1TB", "tech", 120), ("Router", "tech", 200),
    ("Chair", "furniture", 180), ("Desk", "furniture", 250),
    ("Bookshelf", "furniture", 90), ("Footrest", "furniture", 35),
    ("Whiteboard", "office", 55), ("Marker Set", "office", 9),
    ("Cable Ties", "tech", 5), ("Power Strip", "tech", 18),
    ("Filing Cabinet", "furniture", 130), ("Paper Ream", "office", 8),
]

conn = sqlite3.connect(DB_PATH)
conn.execute(
    "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "name TEXT NOT NULL, category TEXT NOT NULL, price TEXT NOT NULL)"
)
conn.execute("DELETE FROM items")
conn.executemany(
    "INSERT INTO items (name, category, price) VALUES (?, ?, ?)",
    [(n, c, str(float(p))) for n, c, p in ITEMS],
)
conn.commit()
print(f"Seeded {len(ITEMS)} items into {DB_PATH}")