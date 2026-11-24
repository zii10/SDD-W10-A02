"""0A 負責：資料存取層（repository.py）的測試。

上面兩個是老師的範例；請在「第一輪」「第二輪」下面加上你的測試。
提示：sample_db 裡有 1 號雨傘（圖書館）、2 號水壺（餐廳）、3 號雨傘（教室）。
"""
import pytest

import repository


# ---------------- 範例（老師提供）----------------
def test_add_item_returns_new_id(db):
    assert repository.add_item(db, "雨傘", "圖書館", "黑傘") == 1


def test_get_item_not_found_returns_none(db):
    assert repository.get_item(db, 99) is None


# ---------------- 第一輪：請從這裡開始加 ----------------


# ---------------- 第二輪：邊界與錯誤情況 ----------------
