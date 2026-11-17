"""0A 第⼀輪的檢查：統計表要有「已認領」欄位。"""
import service
from checklib import check, new_db
db = new_db()
service.report_found(db, "⾬傘", "圖書館")
service.report_found(db, "⾬傘", "餐廳")
service.claim(db, 1, "王⼩明")
rows = {r["類別"]: r for r in service.stats(db)["data"]["rows"]}
check("0A-r1 統計表有已認領欄位", "已認領" in rows["⾬傘"], True)
check("0A-r1 ⾬傘已認領 1 件", rows["⾬傘"].get("已認領"), 1)
check("0A-r1 沒有物品的類別，已認領是 0", rows["鑰匙"].get("已認領"), 0)