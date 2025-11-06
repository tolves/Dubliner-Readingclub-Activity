import os
import json
import datetime as dt
from pathlib import Path
from openai import OpenAI

# ✅ 强制切换到仓库根目录（与你旧脚本保持一致）
os.chdir(Path(__file__).resolve().parent.parent)

# 初始化 OpenAI 客户端
client = OpenAI()

# 仓库根目录
ROOT = Path(".").resolve()
BASE_DIR = ROOT / "scripts"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def find_last_7_days_json():
    """从 data/ 中读取最近 7 天 JSON"""
    data_dir = ROOT / "data"

    if not data_dir.exists():
        raise RuntimeError("❌ data 文件夹不存在")

    today = dt.date.today()
    files = {}

    for i in range(7):
        day = today - dt.timedelta(days=i)
        file_path = data_dir / f"{day.isoformat()}.json"
        if file_path.exists():
            files[day.isoformat()] = load_json(file_path)

    return files


def build_prompt(json_dict):
    """构建 GPT 周报 prompt"""
    year, week, _ = dt.date.today().isocalendar()

    blocks = []
    for date, content in sorted(json_dict.items()):
        blocks.append(f"### {date}\n```\n{content}\n```")

    all_json_blocks = "\n\n".join(blocks)

    prompt = f"""
你是 Dubliner 读书会的记录员。
请基于下面连续7天的每日 JSON 数据，生成一份自然语言但非常详尽的周报（Markdown）。

周报内容必须包含（如无则写“本周无”）：
1. 本周总体概览
2. 新增成员（根据 creator / assignees 中首次出现的用户名）
3. 新增书籍（书名 + 创建者）
4. 完成书籍（整本完成）
5. 阅读进度总结（按书：新增章节、已读完章节、标记未读、是谁阅读的）
6. 成员活跃度（谁最活跃、谁的推进最多）
7. 其他值得记录的变化
8. 下周展望（1–3 句自然语言）

语气自然、温暖、非企业化，不要使用“亮点/阻塞/风险”之类词汇。

最终输出 Markdown，主标题格式：
# Dubliner读书会 · {year}-W{week} 周报

以下是本周每日 JSON 数据：

{all_json_blocks}
"""
    return prompt


def generate_weekly_report(prompt):
    print("⏳ 正在调用 GPT 生成周报...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是擅长阅读进度总结的读书会记录者。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message["content"]


def main():
    print("📚 正在扫描最近 7 天 JSON...")
