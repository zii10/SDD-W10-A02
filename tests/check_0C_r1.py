"""0C 第一輪的檢查：ui.py 有使用說明並顯示在網頁上。
(本機可能沒有安裝gradio，所以這裡直接讀取程式碼檢查，不執行ui.py) """
from checklib import check, read_source

src = read_source("ui.py")
check("0C-r1 有HELP_TEXT", "HELP_TEXT = " in src, True)
check("0C-r1 說明含三種用法", all(w in src for w in ["撿到東西", "找東西", "認領："]), True)
check("0C-r1 網頁有顯示 HELP_TEXT", "gr.Markdown(HELP_TEXT)" in src, True)