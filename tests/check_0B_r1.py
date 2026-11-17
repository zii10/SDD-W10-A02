"""0B 第⼀輪的檢查：描述不可超過 50 字。"""
import service
from checklib import check, new_db
db = new_db()
check("0B-r1 描述剛好 50 字可以登記", service.report_found(db, "水壺", "教室",
"藍" * 50)["ok"], True)
check("0B-r1 描述 51 字要拒絕", service.report_found(db, "水壺", "教室", "藍" *
51)["ok"], False)
check("0B-r1 沒有描述也可以登記", service.report_found(db, "水壺", "教室")["ok"],
True)