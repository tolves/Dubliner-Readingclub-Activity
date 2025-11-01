import os
from pathlib import Path
import glob
import datetime as dt
from openai import OpenAI

# 🔧 切换到仓库根目录
os.chdir(Path(__file__).resolve().parent.parent)

# 使用新版 OpenAI SDK
try:
    from openai import OpenAI
except ImportError:
    raise SystemExit("Please `pip install openai` first.")

def log(msg):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def dublin_now():
    # Actions 步骤里已设置 TZ=Europe/Dublin
    return dt.datetime.now()

def week_range_last_monday_to_this_monday():
    """返回上周一(含) 到 本周一(不含) 的日期范围（都柏林本地）"""
    now = dublin_now().date()
    # 本周一
    this_monday = now - dt.timedelta(days=now.weekday())
    # 上周一
    last_monday = this_monday - dt.timedelta(days=7)
    return last_monday, this_monday

def collect_reports(last_monday, this_monday):
    """读取 reports/ 下 ISO 日期命名的 md 文件，筛选在 [last_monday, this_monday) 的"""
    files = sorted(glob.glob("reports/*.md"))
    picked = []
    for f in files:
        name = os.path.basename(f)
        base = os.path.splitext(name)[0]
        try:
            date = dt.date.fromisoformat(base)  # 文件名形如 2025-11-01.md
        except ValueError:
            continue
        if last_monday <= date < this_monday:
            with open(f, "r", encoding="utf-8") as fh:
                picked.append((date.isoformat(), fh.read()))
    return picked

def build_prompt(week_items, last_monday, this_monday):
    header = (
        f"你是 Dubliner ReadingClub 的记录员，请根据以下【{last_monday} ~ {this_monday - dt.timedelta(days=1)}】期间的每日活动报告，"
        f"总结出一份周报（Markdown 格式）。\n\n"
        f"请从以下角度撰写：\n"
        f"- 本周读书会主要发生了哪些活动或更新。\n"
        f"- 哪些成员最活跃（例如更新或组织活动）。\n"
        f"- 本周主要阅读的书籍或主题方向（可以提及书名、作者、关键词）。\n"
        f"- 若有值得延伸的主题或思考，请简单说明。\n"
        f"- 在最后增加一个“下周推荐”部分，"
        f"基于当前主题给出 1-3 本可延伸阅读的书籍或讨论方向建议。\n\n"
        f"语气应自然、清晰，像读书会内部总结，不要过分文学或企业化。\n\n"
        f"=== 以下为每日报告原文 ===\n"
    )
    body = []
    for date, content in week_items:
        body.append(f"\n## {date}\n\n{content}\n")
    return header + "\n".join(body)

def call_gpt(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set.")
    client = OpenAI(api_key=api_key)
    # 轻量便宜的模型；如需更强可换 gpt-4o
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()

def main():
    log("🚀 Generate weekly summary")
    last_monday, this_monday = week_range_last_monday_to_this_monday()
    log(f"Week window: {last_monday} .. {this_monday} (Europe/Dublin)")

    week_items = collect_reports(last_monday, this_monday)
    log(f"Found {len(week_items)} report files in range.")

    os.makedirs("weekly", exist_ok=True)
    year, week_num, _ = (this_monday - dt.timedelta(days=1)).isocalendar()  # 上周的编号
    weekly_path = f"weekly/{year}-W{week_num:02d}.md"

    if not week_items:
        placeholder = (
            f"# 📅 Dubliner ReadingClub 周报 - {year}-W{week_num:02d}\n\n"
            f"时间范围：{last_monday} ~ {this_monday - dt.timedelta(days=1)}\n\n"
            f"本周未找到日报文件（reports/*.md）。请确认工作流是否生成了每日报告。\n"
        )
        with open(weekly_path, "w", encoding="utf-8") as fh:
            fh.write(placeholder)
        log(f"⚠️ No reports found. Wrote placeholder to {weekly_path}")
        return

    prompt = build_prompt(week_items, last_monday, this_monday)
    summary = call_gpt(prompt)

    with open(weekly_path, "w", encoding="utf-8") as fh:
        fh.write(summary)

    log(f"✅ Weekly summary saved to {weekly_path}")

if __name__ == "__main__":
    main()