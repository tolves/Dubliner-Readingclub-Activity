import os
import json
import datetime as dt
from pathlib import Path
from openai import OpenAI

# ==========================
# 目录初始化
# ==========================
os.chdir(Path(__file__).resolve().parent.parent)
ROOT = Path(".").resolve()

DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
WEEKLY_DIR = ROOT / "weekly"

client = OpenAI()


# ==========================
# 工具函数
# ==========================

def load_json(path):
    """加载 JSON 文件，你的 JSON 是 list 格式。"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print(f"⚠️ 空文件跳过: {path}")
        return None

    try:
        return json.loads(content)
    except Exception as e:
        print(f"⚠️ JSON 解析失败 {path}: {e}")
        return None
        
def load_prompt(path):
    """从文件读取 prompt"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_last_7_days_json():
    """加载最近 7 天 JSON，按日期升序排序。"""
    today = dt.date.today()
    result = {}

    for i in range(7):
        d = today - dt.timedelta(days=i)
        fp = DATA_DIR / f"{d.isoformat()}.json"
        if fp.exists():
            obj = load_json(fp)
            if obj:
                result[d.isoformat()] = obj

    return dict(sorted(result.items(), key=lambda x: x[0]))


def prepare_pairs(days_dict):
    """将 n 天转成 n−1 个 pair：D1→D2, D2→D3 ..."""
    keys = list(days_dict.keys())
    pairs = []

    for i in range(len(keys) - 1):
        day1, day2 = keys[i], keys[i + 1]
        pairs.append((day1, day2, days_dict[day1], days_dict[day2]))

    return pairs


# ==========================
# GPT daily diff（稳定版：纯字符串拼接）
# ==========================

def generate_daily_diff_gpt(day1, day2, json1, json2):
    """从外部 prompt 文件读取 daily diff 模板，并生成对比报告。"""

    # 读取 prompt 模板
    prompt_template = load_prompt(ROOT / "prompts" / "daily_diff.txt")

    # 格式化 JSON
    json1_str = json.dumps(json1, ensure_ascii=False, indent=2)
    json2_str = json.dumps(json2, ensure_ascii=False, indent=2)

    # 注入变量
    prompt = (
        prompt_template
        .replace("{day1}", day1)
        .replace("{day2}", day2)
        .replace("{JSON1}", json1_str)
        .replace("{JSON2}", json2_str)
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你擅长分析 JSON 差异并用自然语言总结。"},
            {"role": "user", "content": prompt},
        ]
    )

    return resp.choices[0].message.content


# ==========================
# GPT weekly summary（同样稳定版）
# ==========================



def generate_weekly_report_gpt(daily_diffs):
    """从 prompt 文件加载模板，并生成周报（采用稳定字符串拼接）"""

    year, week, _ = dt.date.today().isocalendar()

    # 合并 daily diff 文本
    merged = ""
    for d in daily_diffs:
        merged += f"## {d['from']} → {d['to']}\n\n"
        merged += d["diff"] + "\n\n"

    # 加载外部 prompt
    prompt_template = load_prompt(ROOT / "prompts" / "weekly_summary.txt")

    # 注入变量
    prompt = (
        prompt_template
        .replace("{DAILY_DIFFS}", merged)
        .replace("{year}", str(year))
        .replace("{week}", str(week))
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你擅长写自然语言的周报总结。"},
            {"role": "user", "content": prompt},
        ]
    )

    return resp.choices[0].message.content


# ==========================
# 主流程
# ==========================

def main():
    print("📚 正在加载最近 7 天 JSON ...")

    days = load_last_7_days_json()
    if len(days) < 2:
        print("❌ JSON 数量不足，无法生成报告")
        return

    print("✅ 找到天数：", list(days.keys()))
    pairs = prepare_pairs(days)

    daily_diffs = []

    # ----- 逐日 diff -----
    for day1, day2, j1, j2 in pairs:
        print(f"🔍 正在生成 daily diff: {day1} → {day2} ...")

        diff_text = generate_daily_diff_gpt(day1, day2, j1, j2)

        daily_diffs.append({
            "from": day1,
            "to": day2,
            "diff": diff_text
        })

        # 保存 daily 文件
        REPORTS_DIR.mkdir(exist_ok=True)
        out = REPORTS_DIR / f"{day2}_daily_report.md"
        with open(out, "w", encoding="utf-8") as f:
            f.write(f"# {day1} → {day2} 每日阅读变化\n\n")
            f.write(diff_text)

        print(f"✅ 已保存 {out}")

    # ----- 周报 -----
    print("📝 正在生成周报 ...")
    weekly_text = generate_weekly_report_gpt(daily_diffs)

    WEEKLY_DIR.mkdir(exist_ok=True)
    year, week, _ = dt.date.today().isocalendar()
    weekly_path = WEEKLY_DIR / f"{year}-W{week}.md"

    with open(weekly_path, "w", encoding="utf-8") as f:
        f.write(weekly_text)

    print(f"✅ 周报已生成: {weekly_path}")


if __name__ == "__main__":
    main()
