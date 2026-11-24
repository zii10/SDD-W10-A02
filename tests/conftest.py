"""共用的測試工具（老師提供，請勿修改）。

這個檔案裡的 fixture，每個測試檔都可以直接用：
在測試函式的參數寫上它的名字，pytest 就會自動準備好傳進來。

    db         一個全新、空的暫存資料庫（每個測試都拿到不同的一份）
    sample_db  已經登記好 3 件物品的暫存資料庫：
                 1 號：雨傘，圖書館，黑色折疊傘
                 2 號：水壺，餐廳，藍色保溫瓶
                 3 號：雨傘，教室，透明長傘
    fake_ai    做出「照表回答」的假 AI：
                 ask = fake_ai({"我在餐廳撿到一張學生證": "登記|學生證|餐廳"})
"""
import pytest

import ai_parser
import repository


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "test.db")
    repository.init_db(path)
    return path


@pytest.fixture
def sample_db(db):
    repository.add_item(db, "雨傘", "圖書館", "黑色折疊傘")
    repository.add_item(db, "水壺", "餐廳", "藍色保溫瓶")
    repository.add_item(db, "雨傘", "教室", "透明長傘")
    return db


@pytest.fixture
def fake_ai():
    return ai_parser.make_fake_ask
