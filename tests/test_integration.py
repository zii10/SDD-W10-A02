"""0D（加分題 A）：整合測試。從「一句話」經過假 AI，一路測到資料庫。

上面是老師的範例；請加上你的測試。
"""
import service


# ---------------- 範例（老師提供）----------------
def test_register_by_sentence(db, fake_ai):
    ask = fake_ai({"我在餐廳撿到一張學生證": "登記|學生證|餐廳"})
    result = service.handle_message(db, "我在餐廳撿到一張學生證", "", ask)
    assert result["ok"] is True


# ---------------- 請從這裡開始加 ----------------
