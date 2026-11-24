"""0A 第⼆輪的檢查：類別清單要有「眼鏡」，⽽且可以登記。"""
import service
from config import CATEGORIES
from checklib import check, new_db
db = new_db()
check("0A-r2 類別清單有眼鏡", "眼鏡" in CATEGORIES, True)
check("0A-r2 可以登記眼鏡", service.report_found(db, "眼鏡", "操場")["ok"],
True)
check("0A-r2 「其他」仍然是最後⼀個類別", CATEGORIES[-1], "其他")