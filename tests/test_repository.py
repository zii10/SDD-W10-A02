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
def test_get_item_returns_expected_fields(sample_db):
    item = repository.get_item(sample_db, 2)
    assert item is not None
    assert item["category"] == "水壺"
    assert item["location"] == "餐廳"
    assert item["status"] == "待認領"
    assert item["claimer"] is None


def test_find_items_by_category(sample_db):
    items = repository.find_items(sample_db, category="雨傘")
    assert [it["id"] for it in items] == [1, 3]


def test_mark_claimed_updates_status(sample_db):
    assert repository.mark_claimed(sample_db, 1, "王小明") is True
    item = repository.get_item(sample_db, 1)
    assert item["status"] == "已認領"
    assert item["claimer"] == "王小明"


# ---------------- 第二輪：邊界與錯誤情況 ----------------
def test_find_items_no_match_returns_empty_list(sample_db):
    items = repository.find_items(sample_db, category="手機")
    assert items == []


def test_mark_claimed_nonexistent_item_returns_false(sample_db):
    assert repository.mark_claimed(sample_db, 99, "王小明") is False


def test_mark_claimed_already_claimed_item_returns_false(sample_db):
    assert repository.mark_claimed(sample_db, 1, "王小明") is True
    # 同一件物品已被認領，再次認領應失敗
    assert repository.mark_claimed(sample_db, 1, "李小華") is False
