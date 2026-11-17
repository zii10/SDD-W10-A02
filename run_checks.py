"""一次跑完所有檢查：分層健康檢查 + tests/ 裡的每個 check_*.py。
用法：在 repo 資料夾的終端機輸入  python run_checks.py
全部通過時結束碼為 0；有任何失敗時為 1（W12 的 CI 會用到）。"""
import glob
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

import checklib

print("== 衝突標記檢查 ==")
markers = checklib.find_conflict_markers()
if markers:
    for filename, no, line in markers:
        print(f"還沒解完的衝突：{filename} 第 {no} 行 → {line}")
    print("請刪掉 <<<<<<<、=======、>>>>>>> 這三種標記，保留正確的內容後再執行一次。")
    sys.exit(1)
print("沒有殘留的衝突標記")

print("\n== 分層健康檢查 ==")
layer_problems = checklib.check_layers()

crashed = []
for path in sorted(glob.glob(os.path.join("tests", "check_*.py"))):
    print(f"\n== {path} ==")
    try:
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"ERROR 這個檢查檔執行時出錯：{type(e).__name__}: {e}")
        crashed.append(path)

passed = sum(1 for ok in checklib.RESULTS.values() if ok)
failed = [name for name, ok in checklib.RESULTS.items() if not ok]
print("\n================ 總結 ================")
print(f"通過 {passed} 項，失敗 {len(failed)} 項，出錯的檢查檔 {len(crashed)} 個，越界 {layer_problems} 處")
for name in failed:
    print("  失敗：", name)
for path in crashed:
    print("  出錯：", path)
all_ok = (not failed) and (not crashed) and layer_problems == 0
print("結果：", "全部通過" if all_ok else "尚未通過")
sys.exit(0 if all_ok else 1)
