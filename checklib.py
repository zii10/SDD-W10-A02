"""測試小工具（老師提供，請勿修改）。tests/ 裡的每個檢查檔都用這裡的 check()。"""
import os
import tempfile

RESULTS = {}

LAYER_RULES = {
    "repository.py": ["import service", "import ai_parser", "import ui", "gradio", "groq", "client."],
    "ai_parser.py": ["sqlite3", "import repository", "import service", "import ui", "gradio"],
    "service.py": ["sqlite3", "SELECT ", "INSERT ", "UPDATE ", "gradio", "groq", "client."],
    "ui.py": ["sqlite3", "SELECT ", "import repository", "import ai_parser", "groq", "client."],
}


def check(name, actual, expected):
    ok = (actual == expected)
    print(("PASS  " if ok else "FAIL  ") + name +
          ("" if ok else f"（預期 {expected!r}，實際 {actual!r}）"))
    RESULTS[name] = ok


def new_db():
    """建立一個全新的暫存資料庫，回傳路徑。"""
    import repository
    path = os.path.join(tempfile.mkdtemp(), "test.db")
    repository.init_db(path)
    return path


def read_source(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


def find_conflict_markers():
    """找出所有 .py 檔裡沒刪乾淨的衝突標記。"""
    import glob
    found = []
    for filename in sorted(glob.glob("*.py") + glob.glob(os.path.join("tests", "*.py"))):
        for no, line in enumerate(read_source(filename).splitlines(), start=1):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                found.append((filename, no, line.strip()))
    return found


def check_layers():
    problems = 0
    for filename, banned in LAYER_RULES.items():
        for no, line in enumerate(read_source(filename).splitlines(), start=1):
            code_part = line.split("#")[0]
            for word in banned:
                if word in code_part:
                    print(f"越界：{filename} 第 {no} 行出現「{word.strip()}」")
                    problems += 1
    print("分層健康檢查：", "通過" if problems == 0 else f"發現 {problems} 個問題")
    return problems
