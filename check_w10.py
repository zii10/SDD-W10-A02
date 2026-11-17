"""W10 進度自我檢查：讀取這個 repo 在 GitHub 上的紀錄，逐項回報完成狀態。
用法：在 repo 資料夾的終端機輸入  python check_w10.py
（會先執行 git fetch 取得 GitHub 上的最新狀態，不會修改任何檔案。）"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


code, _ = git("fetch", "origin", "--prune", "--tags", "--quiet")
if code != 0:
    print("無法連到 GitHub（git fetch 失敗）。請確認網路與登入狀態後再試。")
    sys.exit(1)

code, _ = git("rev-parse", "--verify", "origin/main")
if code != 0:
    print("找不到 origin/main。請確認組長已把版本 0 推到 main。")
    sys.exit(1)

# 1. 從 main 上的合併紀錄找出 PR（GitHub 合併 PR 時的訊息是「Merge pull request #N from 帳號/分支」）
_, merges = git("log", "origin/main", "--merges", "--format=%s")
pr_branches = []
for line in merges.splitlines():
    m = re.match(r"Merge pull request #\d+ from [^/]+/(\S+)", line)
    if m:
        pr_branches.append(m.group(1))

members = sorted({b[:2] for b in pr_branches if re.match(r"0[ABC]-r[12]$", b)})
r1 = sorted(b for b in pr_branches if re.match(r"0[ABC]-r1$", b))
r2 = sorted(b for b in pr_branches if re.match(r"0[ABC]-r2$", b))
r3 = sorted(b for b in pr_branches if re.match(r"0[ABC]-r3$", b))
odd = [b for b in pr_branches if not re.match(r"0[ABC]-r[123]$", b)]

# 2. 解衝突的紀錄：把 main 合進自己分支時產生的合併
_, all_merges = git("log", "origin/main", "--merges", "--format=%s")
conflict_merges = [s for s in all_merges.splitlines()
                   if re.match(r"Merge (branch 'main'|remote-tracking branch 'origin/main')", s)]

# 3. 直接推到 main 的 commit（不是透過 PR）
# 第一個 PR 合併之前的 commit 屬於「建立版本 0」，不算
_, first_parent = git("log", "origin/main", "--first-parent", "--reverse", "--format=%h|%P|%s")
direct, seen_pr = [], False
for line in first_parent.splitlines():
    h, parents, subject = line.split("|", 2)
    is_merge = len(parents.split()) > 1
    if is_merge and subject.startswith("Merge pull request"):
        seen_pr = True
    elif seen_pr and not is_merge:
        direct.append(f"{h} {subject}")

# 4. 作者
_, authors = git("log", "origin/main", "--no-merges", "--format=%an <%ae>")
author_set = sorted(set(authors.splitlines()))

# 5. tag v1（加分題另有 v2）
def tag_on_main(tag):
    return (git("rev-parse", "--verify", f"refs/tags/{tag}")[0] == 0
            and git("merge-base", "--is-ancestor", tag, "origin/main")[0] == 0)

v1_on_main = tag_on_main("v1")
v2_on_main = tag_on_main("v2")

# 6. 本機的 main 是否跟上 GitHub
_, local_branch = git("rev-parse", "--abbrev-ref", "HEAD")
_, behind = git("rev-list", "--count", "HEAD..origin/main")

n = max(len(members), 1)
items = [
    (f"偵測到的組員分支代號：{', '.join(members) or '（無）'}", len(members) >= 2),
    (f"第一輪已合併的 PR：{', '.join(r1) or '（無）'}（每位組員 1 個）", len(r1) >= n and len(members) >= 2),
    (f"第二輪已合併的 PR：{', '.join(r2) or '（無）'}（每位組員 1 個）", len(r2) >= n and len(members) >= 2),
    (f"解衝突的合併紀錄：{len(conflict_merges)} 筆（至少 1 筆）", len(conflict_merges) >= 1),
    (f"沒有繞過 PR 直接推到 main 的 commit（發現 {len(direct)} 個）", len(direct) == 0),
    ("已建立 tag v1，且在 main 上", v1_on_main),
]

print("=========== W10 進度檢查 ===========")
for text, ok in items:
    print(("[完成] " if ok else "[未完成] ") + text)

missing_r2 = [m for m in members if f"{m}-r2" not in r2]
if missing_r2 == ["0C"]:
    print("\n說明：只差 0C 的第二輪。如果老師宣布 0C 第二輪為選做，這一項可以忽略。")

if r3 or v2_on_main:
    print("\n----------- 加分題（第三輪）-----------")
    print(("[完成] " if len(r3) >= n else "[未完成] ") + f"第三輪已合併的 PR：{', '.join(r3) or '（無）'}（每位組員 1 個）")
    print(("[完成] " if v2_on_main else "[未完成] ") + "已建立 tag v2，且在 main 上")

if odd:
    print("\n注意：這些 PR 的分支名稱不符合規則（應為 0A-r1、0B-r2、0C-r3 這種格式）：", ", ".join(odd))
if direct:
    print("\n注意：下列 commit 直接出現在 main 上，沒有經過 PR：")
    for line in direct[:5]:
        print("   ", line)
print("\ncommit 作者（請確認每位組員都在，且 email 與自己的 GitHub 帳號一致）：")
for a in author_set:
    print("   ", a)
if local_branch == "main" and behind not in ("", "0"):
    print(f"\n提醒：你本機的 main 落後 GitHub {behind} 個 commit，請先執行 git pull。")
print("\n合併後的程式是否正常，請另外執行：python run_checks.py")
