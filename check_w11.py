"""W11 進度自我檢查（老師提供，請勿修改）。
用法：在 repo 資料夾的終端機輸入  python check_w11.py

它會先執行 git fetch 取得 GitHub 上的最新狀態，再把 GitHub 上的 main 另外取出一份來跑 pytest，
所以檢查的是「GitHub 上的 main」，不是你電腦裡改到一半的檔案。不會修改任何檔案。"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

REQUIRED_FILES = ["tests/test_repository.py", "tests/test_service.py", "tests/test_ai_parser.py"]
MIN_TESTS = 5


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


def export(ref, folder):
    """把 GitHub 上某個版本的檔案取出到 folder（不動到你的工作資料夾）。"""
    r = subprocess.run(["git", "archive", "--format=zip", ref], capture_output=True)
    if r.returncode != 0:
        return False
    zipfile.ZipFile(io.BytesIO(r.stdout)).extractall(folder)
    return True


def pytest_at(folder, *extra):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *extra],
                       cwd=folder, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return r.returncode, r.stdout + r.stderr


def count_tests(folder):
    code, out = pytest_at(folder, "--collect-only")
    counts = {}
    for line in out.splitlines():
        m = re.match(r"(tests/test_\w+\.py)::", line.replace("\\", "/"))
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    return counts


def tag_on_main(tag):
    return (git("rev-parse", "--verify", f"refs/tags/{tag}")[0] == 0
            and git("merge-base", "--is-ancestor", tag, "origin/main")[0] == 0)


code, _ = git("fetch", "origin", "--prune", "--tags", "--force", "--quiet")
if code != 0:
    print("無法連到 GitHub（git fetch 失敗）。請確認網路與登入狀態後再試。")
    sys.exit(1)

_, merges = git("log", "origin/main", "--merges", "--format=%s")
merged = set()
for line in merges.splitlines():
    m = re.match(r"Merge pull request #\d+ from [^/]+/(\S+)", line)
    if m:
        merged.add(m.group(1))

work = tempfile.mkdtemp(prefix="w11_check_")
try:
    main_dir = os.path.join(work, "main")
    export("origin/main", main_dir)
    has_kit = os.path.exists(os.path.join(main_dir, "pytest.ini"))
    counts = count_tests(main_dir) if has_kit else {}
    passed = pytest_at(main_dir)[0] == 0 if has_kit else False

    r1 = [b for b in ("t1-0A", "t1-0B", "t1-0C") if b in merged]
    r2 = [b for b in ("t2-0A", "t2-0B", "t2-0C") if b in merged]
    enough = {f: counts.get(f, 0) for f in REQUIRED_FILES}

    items = [
        ("W11 套件已合併（main 上有 pytest.ini）", has_kit),
        (f"第一輪已合併的 PR：{', '.join(r1) or '（無）'}（需要 t1-0A、t1-0B、t1-0C）", len(r1) == 3),
        (f"第二輪已合併的 PR：{', '.join(r2) or '（無）'}（需要 t2-0A、t2-0B、t2-0C）", len(r2) == 3),
        ("三個測試檔各至少 5 個測試：" + "、".join(f"{f.split('/')[1]} {n} 個" for f, n in enough.items()),
         all(n >= MIN_TESTS for n in enough.values())),
        ("GitHub 上的 main 執行 pytest 全部通過", passed),
        ("已建立 tag w11，且在 main 上", tag_on_main("w11")),
    ]
    print("=========== W11 進度檢查（看的是 GitHub 上的 main）===========")
    for text, ok in items:
        print(("[完成] " if ok else "[未完成] ") + text)

    bonus_a = any(b in merged for b in ("t1-0D", "t2-0D"))
    n_int = counts.get("tests/test_integration.py", 0)
    bonus_b_fix = [b for b in ("fix-0A", "fix-0B", "fix-0C") if b in merged]
    has_vendor = os.path.exists(os.path.join(main_dir, "VERSION"))
    issue_tests = [f for f in ("tests/test_issue_0A.py", "tests/test_issue_0B.py", "tests/test_issue_0C.py")
                   if os.path.exists(os.path.join(main_dir, f))]
    if bonus_a or n_int > 1 or has_vendor or bonus_b_fix:
        print("\n----------- 加分題 -----------")
        print(("[完成] " if (bonus_a and n_int >= MIN_TESTS) else "[未完成] ")
              + f"加分 A（0D 整合測試）：PR {'已合併' if bonus_a else '未合併'}，test_integration.py {n_int} 個測試")
        ok_b = has_vendor and len(bonus_b_fix) == 3 and len(issue_tests) == 3 and tag_on_main("w11-bonus")
        print(("[完成] " if ok_b else "[未完成] ")
              + f"加分 B（廠商更新）：更新已合併到 main {'是' if has_vendor else '否'}；"
              f"修正 PR {', '.join(bonus_b_fix) or '（無）'}；回歸測試檔 {len(issue_tests)}/3；"
              f"tag w11-bonus {'有' if tag_on_main('w11-bonus') else '沒有'}")

    if not passed and has_kit:
        print("\nmain 上的 pytest 沒有全過。請在自己電腦 git switch main、git pull 後執行 python -m pytest 看是哪一個。")
    odd = sorted(b for b in merged if re.match(r"t\d", b) and not re.match(r"t[12]-0[ABCD]$", b))
    if odd:
        print("\n注意：這些 PR 的分支名稱不符合規則（應為 t1-0A、t2-0B 這種格式）：", ", ".join(odd))

    _, authors = git("log", "origin/main", "--format=%an <%ae>")
    print("\n出現在 main 歷史中的人（commit 作者，以及在網頁上按合併的人）：")
    for a in sorted(set(authors.splitlines())):
        print("   ", a)
finally:
    shutil.rmtree(work, ignore_errors=True)
