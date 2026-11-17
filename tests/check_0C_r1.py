"""0C 第⼀輪的檢查：ui.py 有使⽤說明並顯⽰在網⾴上。
（本機可能沒有安裝gradio，所以這裡直接讀程式碼檢查，不執⾏ui.py。"""
from checklib import check, read_source
src = read_source("ui.py")
check("0C-r1 有HELP_TEXT", "HELP_TEXT = " in src, True)
check("0C-r1 說明含三種⽤法", all(w in src for w in ["撿到東⻄", "找東⻄", "認領："]), True)
check("0C-r1 網⾴有顯⽰ HELP_TEXT", "gr.Markdown(HELP_TEXT)" in src, True)