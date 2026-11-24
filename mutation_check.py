"""練習用的「植入錯誤」檢查（老師提供，請勿修改）。

用法（在 repo 資料夾的終端機）：
    python mutation_check.py            檢查全部 9 個練習 mutant
    python mutation_check.py 0B         只檢查 0B 負責的那一層

做法：把程式複製一份到暫存資料夾，故意改壞一個地方（一個 mutant），再執行 pytest。
如果有測試因此 FAIL，代表你的測試「抓到」了這個錯誤；全部 PASS 就是「沒抓到」，
表示還缺少能發現這種錯誤的測試。不會修改你 repo 裡的任何檔案。

評分時老師會用另一組「隱藏」的 mutant，所以不要只針對這 9 個寫測試，
要想想每一層還有哪些地方可能寫錯。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

MUTANTS = [{'id': 'P-R1',
  'layer': '0A',
  'file': 'repository.py',
  'desc': '統計表把 LEFT JOIN 改成 JOIN（沒有物品的類別會消失）',
  'old': 'LEFT JOIN items i',
  'new': 'JOIN items i'},
 {'id': 'P-R2',
  'layer': '0A',
  'file': 'repository.py',
  'desc': '查詢時不再排除已認領的物品',
  'old': 'FROM items WHERE status = \'待認領\'"',
  'new': 'FROM items WHERE 1 = 1"'},
 {'id': 'P-R3',
  'layer': '0A',
  'file': 'repository.py',
  'desc': '已認領的物品還能再被標記為已認領',
  'old': '"WHERE id = ? AND status = \'待認領\'", (claimer, item_id))',
  'new': '"WHERE id = ?", (claimer, item_id))'},
 {'id': 'P-S1',
  'layer': '0B',
  'file': 'service.py',
  'desc': '每人上限少算一件（可以認領 3 件）',
  'old': '>= MAX_CLAIMS_PER_PERSON:',
  'new': '> MAX_CLAIMS_PER_PERSON:'},
 {'id': 'P-S2',
  'layer': '0B',
  'file': 'service.py',
  'desc': '描述的長度限制從 50 字變成 60 字',
  'old': 'len(description) > 50',
  'new': 'len(description) > 60'},
 {'id': 'P-S3',
  'layer': '0B',
  'file': 'service.py',
  'desc': '登記時不再檢查地點是否在清單內',
  'old': 'if location not in LOCATIONS:',
  'new': 'if location is None:'},
 {'id': 'P-A1',
  'layer': '0C',
  'file': 'ai_parser.py',
  'desc': '物品編號改從 AI 的回覆抓，而不是使用者的原話',
  'old': 'm = re.search(r"\\d+", user_text)',
  'new': 'm = re.search(r"\\d+", reply)'},
 {'id': 'P-A2',
  'layer': '0C',
  'file': 'ai_parser.py',
  'desc': '回覆裡出現兩個類別時，不再取最早出現的那一個',
  'old': 'if pos != -1 and pos < best_pos:',
  'new': 'if pos != -1:'},
 {'id': 'P-A3',
  'layer': '0C',
  'file': 'ai_parser.py',
  'desc': 'AI 沒說動作時，預設成「查詢」而不是「未知」',
  'old': '"action": action or "未知"',
  'new': '"action": action or "查詢"'}]

LAYER_NAME = {"0A": "資料存取層 repository.py", "0B": "商業規則層 service.py", "0C": "AI 解讀層 ai_parser.py"}


def run_pytest(folder):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"],
                           cwd=folder, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return 1, "逾時"
    return r.returncode, r.stdout + r.stderr


def copy_repo(dst):
    shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.db", ".pytest_cache"))


def main():
    only = sys.argv[1].upper() if len(sys.argv) > 1 else None
    if only and only not in LAYER_NAME:
        print("用法：python mutation_check.py [0A|0B|0C]")
        sys.exit(2)
    work = tempfile.mkdtemp(prefix="w11_mut_")
    try:
        base = os.path.join(work, "base")
        copy_repo(base)
        code, out = run_pytest(base)
        if code == 5:
            print("找不到任何測試。請確認 pytest.ini 與 tests 資料夾都在 repo 裡。")
            sys.exit(1)
        if code != 0:
            print("你的程式在「沒有改壞」的情況下，pytest 就已經沒有全過。")
            print("請先執行 python -m pytest，讓所有測試都通過，再來做 mutant 檢查。\n")
            print("\n".join(out.strip().splitlines()[-15:]))
            sys.exit(1)

        rows = []
        for m in MUTANTS:
            if only and m["layer"] != only:
                continue
            folder = os.path.join(work, m["id"])
            copy_repo(folder)
            path = os.path.join(folder, m["file"])
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if text.count(m["old"]) != 1:
                rows.append((m, "略過"))
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.replace(m["old"], m["new"]))
            code, _ = run_pytest(folder)
            rows.append((m, "抓到" if code != 0 else "沒抓到"))
            shutil.rmtree(folder, ignore_errors=True)

        print("=========== 練習用 mutant 檢查 ===========")
        for layer in ["0A", "0B", "0C"]:
            part = [(m, r) for m, r in rows if m["layer"] == layer]
            if not part:
                continue
            caught = sum(1 for _, r in part if r == "抓到")
            print(f"\n{layer} {LAYER_NAME[layer]}：抓到 {caught}/{len(part)}")
            for m, r in part:
                mark = {"抓到": "[抓到]  ", "沒抓到": "[沒抓到]", "略過": "[略過]  "}[r]
                print(f"  {mark} {m['id']}  {m['desc']}")
        total = [r for _, r in rows if r != "略過"]
        print(f"\n合計：抓到 {total.count('抓到')}/{len(total)}")
        if "沒抓到" in total:
            print("「沒抓到」的項目：請想一個測試，在程式被這樣改壞時會 FAIL，正常時會 PASS。")
        if any(r == "略過" for _, r in rows):
            print("「略過」：你們的程式和範本寫法不同，這個 mutant 套不上去，不影響結果。")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
