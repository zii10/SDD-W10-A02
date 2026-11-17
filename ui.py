"""介面層（UI）：只負責畫面，把使用者輸入交給 service，再把結果顯示出來。

這一層的規矩：
- 不寫 SQL、不呼叫 Groq、不判斷商業規則。
- 只認識 service，不認識 repository 和 ai_parser。
"""
import gradio as gr
import pandas as pd
import service


def build_demo(db_path, ask_fn):
    def on_submit(user_text, claimer):
        result = service.handle_message(db_path, user_text, claimer, ask_fn)
        mark = "【完成】" if result["ok"] else "【無法處理】"
        return mark + result["message"]

    def on_stats():
        return pd.DataFrame(service.stats(db_path)["data"]["rows"])

    with gr.Blocks(title="校園失物招領") as demo:
        gr.Markdown("# 校園失物招領系統")
        msg = gr.Textbox(label="請輸入（例如：我在圖書館撿到一把雨傘／我要認領 1 號）")
        name = gr.Textbox(label="認領人姓名（認領時填寫）")
        send = gr.Button("送出")
        out = gr.Textbox(label="系統回覆", lines=5)
        stats_btn = gr.Button("看統計")
        table = gr.Dataframe()
        send.click(on_submit, inputs=[msg, name], outputs=out)
        stats_btn.click(on_stats, outputs=table)
    return demo
