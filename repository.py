"""資料存取層（Repository）：只負責和資料庫打交道。

這一層的規矩：
- 只寫 SQL，一律用 ? 參數。
- 不判斷商業規則（例如「已認領不能再認領」不寫在這裡）。
- 不呼叫 AI、不處理畫面。
"""
import sqlite3
from config import CATEGORIES


def init_db(db_path):
    """每次都刪掉舊表重建，避免依賴舊的 .db 檔。"""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE IF EXISTS items")
        conn.execute("DROP TABLE IF EXISTS categories")
        conn.execute("CREATE TABLE categories (name TEXT PRIMARY KEY)")
        conn.execute("""
            CREATE TABLE items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT '待認領',
                claimer TEXT
            )""")
        conn.executemany("INSERT INTO categories (name) VALUES (?)",
                         [(c,) for c in CATEGORIES])
        conn.commit()
    finally:
        conn.close()


def add_item(db_path, category, location, description):
    """新增一筆拾獲物品，回傳新編號。"""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO items (category, location, description) VALUES (?, ?, ?)",
            (category, location, description))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_item(db_path, item_id):
    """依編號找一筆物品；找不到回傳 None。"""
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT id, category, location, description, status, claimer "
            "FROM items WHERE id = ?", (item_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return {"id": row[0], "category": row[1], "location": row[2],
            "description": row[3], "status": row[4], "claimer": row[5]}


def find_items(db_path, category=None, location=None):
    """找待認領的物品；category、location 是 None 時代表不限。"""
    sql = "SELECT id, category, location FROM items WHERE status = '待認領'"
    params = []
    if category is not None:
        sql += " AND category = ?"
        params.append(category)
    if location is not None:
        sql += " AND location = ?"
        params.append(location)
    sql += " ORDER BY id"
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "category": r[1], "location": r[2]} for r in rows]


def mark_claimed(db_path, item_id, claimer):
    """把物品改成已認領；成功回傳 True。"""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "UPDATE items SET status = '已認領', claimer = ? "
            "WHERE id = ? AND status = '待認領'", (claimer, item_id))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def count_claimed_by(db_path, claimer):
    """這個人已經認領了幾件（練習 B 會用到）。"""
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM items WHERE claimer = ?", (claimer,)).fetchone()
    finally:
        conn.close()
    return row[0]


def category_stats(db_path):
    """各類別的物品件數與待認領件數；沒有物品的類別也要列出（LEFT JOIN）。"""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("""
            SELECT c.name,
                   COUNT(i.id),
                   COUNT(CASE WHEN i.status = '待認領' THEN 1 END)
            FROM categories c
            LEFT JOIN items i ON i.category = c.name
            GROUP BY c.name
            ORDER BY c.rowid""").fetchall()
    finally:
        conn.close()
    return [{"類別": r[0], "總件數": r[1], "待認領": r[2]} for r in rows]
