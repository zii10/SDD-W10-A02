"""商業規則層（Service）：系統「該怎麼做」都寫在這裡。

這一層的規矩：
- 不寫 SQL（交給 repository）。
- 不直接呼叫 Groq（AI 函式由外面傳進來，叫做 ask_fn）。
- 不處理畫面。
- 每個功能都回傳 {"ok": True/False, "message": 給使用者看的話, "data": 其他資料}。
"""
import repository as repo
import ai_parser
from config import CATEGORIES, LOCATIONS, MAX_CLAIMS_PER_PERSON


def _result(ok, message, data=None):
    return {"ok": ok, "message": message, "data": data}


def report_found(db_path, category, location, description=""):
    """登記拾獲物品。"""
    if category not in CATEGORIES:
        return _result(False, "請說明是什麼物品（例如：雨傘、水壺、學生證）。")
    if location not in LOCATIONS:
        return _result(False, "請說明在哪裡撿到的（例如：圖書館、餐廳）。")
    new_id = repo.add_item(db_path, category, location, description)
    return _result(True, f"已登記：{location}撿到的{category}，編號 {new_id}。請送到系辦。",
                   {"id": new_id})


def search(db_path, category=None, location=None):
    """查詢待認領物品。"""
    if category is None and location is None:
        return _result(False, "請說明要找什麼物品，或在哪裡遺失的。")
    items = repo.find_items(db_path, category, location)
    if not items:
        return _result(True, "目前沒有符合的待認領物品。", {"items": []})
    lines = [f"編號 {it['id']}：{it['location']}的{it['category']}" for it in items]
    return _result(True, "找到以下待認領物品：\n" + "\n".join(lines), {"items": items})


def claim(db_path, item_id, claimer):
    """認領物品。"""
    if item_id is None:
        return _result(False, "請提供物品編號，例如：我要認領 3 號。")
    if claimer is None or claimer.strip() == "":
        return _result(False, "請填寫認領人姓名。")
    claimer = claimer.strip()
    item = repo.get_item(db_path, item_id)
    if item is None:
        return _result(False, f"找不到編號 {item_id} 的物品。")
    if item["status"] != "待認領":
        return _result(False, f"編號 {item_id} 已經被認領了。")
    # 練習 B：每人上限
    if repo.count_claimed_by(db_path, claimer) >= MAX_CLAIMS_PER_PERSON:
        return _result(False, f"{claimer} 已認領 {MAX_CLAIMS_PER_PERSON} 件，已達上限。")
    if not repo.mark_claimed(db_path, item_id, claimer):
        return _result(False, "認領失敗，請再試一次。")
    return _result(True, f"{claimer} 已認領編號 {item_id}（{item['category']}），請帶證件到系辦領取。",
                   {"id": item_id})


def stats(db_path):
    """各類別統計。"""
    return _result(True, "各類別統計", {"rows": repo.category_stats(db_path)})


def handle_message(db_path, user_text, claimer, ask_fn):
    """整合入口：一句話 → AI 解讀 → 對應的功能。"""
    if user_text is None or user_text.strip() == "":
        return _result(False, "請輸入內容。")
    parsed = ai_parser.parse_message(user_text, ask_fn)
    category = None if parsed["category"] == "未知" else parsed["category"]
    location = None if parsed["location"] == "未知" else parsed["location"]
    if parsed["action"] == "登記":
        return report_found(db_path, category, location, user_text)
    if parsed["action"] == "查詢":
        return search(db_path, category, location)
    if parsed["action"] == "認領":
        return claim(db_path, parsed["item_id"], claimer)
    return _result(False, "看不懂您的需求，請說明是要登記、查詢還是認領。")
