"""版本 0 的基本檢查（老師提供）。合併任何人的修改後，這些都必須仍然通過。"""
import ai_parser
import service
from config import CATEGORIES
from checklib import check, new_db

db = new_db()
check("base-1 登記雨傘", service.report_found(db, "雨傘", "圖書館")["ok"], True)
check("base-2 不在清單的類別要拒絕", service.report_found(db, "飛機", "圖書館")["ok"], False)
check("base-3 認領 1 號", service.claim(db, 1, "王小明")["ok"], True)
check("base-4 1 號不能再被認領", service.claim(db, 1, "李小華")["ok"], False)
check("base-5 統計表列出每一個類別", len(service.stats(db)["data"]["rows"]), len(CATEGORIES))

db = new_db()
for cat in ["雨傘", "水壺", "耳機"]:
    service.report_found(db, cat, "教室")
service.claim(db, 1, "王小明")
service.claim(db, 2, "王小明")
check("base-6 每人最多認領 2 件", service.claim(db, 3, "王小明")["ok"], False)

fake = ai_parser.make_fake_ask({"我在餐廳撿到一張學生證": "登記|學生證|餐廳"})
db = new_db()
check("base-7 假 AI 一句話登記", service.handle_message(db, "我在餐廳撿到一張學生證", "", fake)["ok"], True)
check("base-8 AI 沒回覆時不處理", service.handle_message(db, "看不懂的話", "", fake)["ok"], False)
