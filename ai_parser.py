"""AI 解讀層：把使用者的一句話，轉成程式看得懂的欄位。

這一層的規矩：
- 不碰資料庫、不判斷商業規則。
- AI 的回覆一律「不直接相信」：從回覆中找允許清單裡的值，找不到就當「未知」。
- 真的 AI 與假的 AI 都是「給一句話、回一行字」的函式，可以互換。
"""
import re
import time
from config import ACTIONS, CATEGORIES, LOCATIONS

SYSTEM_PROMPT = f"""你是校園失物招領系統的解讀助手。請從使用者的話判斷三件事：
1. 動作：登記（撿到東西要交出）、查詢（找自己掉的東西）、認領（要領回某個編號的物品）
2. 物品類別：{"、".join(CATEGORIES)}
3. 地點：{"、".join(LOCATIONS)}
只回覆一行，格式：動作|類別|地點
看不出來的欄位寫「未知」。不要解釋。"""


def make_groq_ask(client, model, reasoning_effort="low", max_retries=2):
    """真的 AI：回傳一個 ask(使用者的話) 函式。失敗時回傳空字串。"""
    def ask(user_text):
        for attempt in range(max_retries + 1):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT},
                              {"role": "user", "content": user_text}],
                    reasoning_effort=reasoning_effort)
                return resp.choices[0].message.content or ""
            except Exception as e:
                if "429" in str(e) and attempt < max_retries:
                    time.sleep(5 * (attempt + 1))   # 額度用完，等一下再試
                    continue
                print("AI 呼叫失敗：", type(e).__name__)
                return ""
        return ""
    return ask


def make_fake_ask(answers):
    """假 AI（照表回答）：answers 是 {使用者的話: AI 回覆}。不在表上就回空字串。"""
    def ask(user_text):
        return answers.get(user_text, "")
    return ask


def make_keyword_ask():
    """假 AI（關鍵字版）：不呼叫 Groq，用關鍵字湊出和真 AI 同格式的回覆。"""
    def ask(user_text):
        # 檢查順序很重要：先找「認領」，再找查詢的說法（「有人撿到」也是查詢），最後才找「撿到」
        if "認領" in user_text:
            action = "認領"
        elif any(w in user_text for w in ["有人撿到", "掉", "找", "遺失", "不見"]):
            action = "查詢"
        elif "撿到" in user_text or "拾獲" in user_text:
            action = "登記"
        else:
            action = "未知"
        category = _find_first(user_text, CATEGORIES) or "未知"
        location = _find_first(user_text, LOCATIONS) or "未知"
        return f"{action}|{category}|{location}"
    return ask


def _find_first(text, candidates):
    """回傳 candidates 中最早出現在 text 裡的那一個；都沒有就回傳 None。"""
    best, best_pos = None, len(text) + 1
    for c in candidates:
        pos = text.find(c)
        if pos != -1 and pos < best_pos:
            best, best_pos = c, pos
    return best


def parse_reply(reply, user_text):
    """把 AI 的回覆整理成欄位（不直接相信 AI）。"""
    parts = reply.split("|") if reply else []
    action = _find_first(parts[0], ACTIONS) if len(parts) > 0 else None
    category = _find_first(parts[1], CATEGORIES) if len(parts) > 1 else None
    location = _find_first(parts[2], LOCATIONS) if len(parts) > 2 else None
    # 安全網：物品編號只從使用者的原話抓，不採用 AI 給的數字
    m = re.search(r"\d+", user_text)
    item_id = int(m.group()) if m else None
    return {"action": action or "未知",
            "category": category or "未知",
            "location": location or "未知",
            "item_id": item_id}


def parse_message(user_text, ask_fn):
    """一句話 → 問 AI → 整理成欄位。"""
    return parse_reply(ask_fn(user_text), user_text)
