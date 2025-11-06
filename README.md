📚 Dubliner Reading Club Activity

自动生成 每日阅读进度报告 & 每周读书会周报

✨ 主要功能

✅ 每日阅读变化对比（Daily Diff）
自动比较前一天与当天的 ClickUp 任务 JSON，生成自然语言阅读进度报告。
✅ 每周总结（Weekly Summary）
汇总过去 7 天的变化，生成结构化、自然语言的读书会周报。
✅ GitHub Actions 自动化
每周一自动运行脚本，生成报告并自动 push 到仓库。
✅ Prompt 模板可独立编辑
所有生成规则均在 prompts/ 中，可随时调语气、风格，无需修改代码。

🗂️ 目录结构
scripts/                 # 主脚本
prompts/                 # Prompt 模板
reports/                 # 自动生成的每日阅读报告
weekly/                  # 自动生成的周报
data/                    # 本地 JSON 快照（不提交）

🚀 本地运行
pip install openai
export OPENAI_API_KEY="你的 key"
python scripts/weekly_summary.py

运行后生成：
reports/YYYY-MM-DD_daily_report.md
weekly/YYYY-Wxx.md

🤖 GitHub Actions 自动化运行
仓库包含：
.github/workflows/weekly.yml
自动负责：
  拉取代码
  安装依赖
  生成 daily diff
  生成 weekly summary
  分两次 push（daily / weekly 分开提交）

✏️ 编辑 Prompt（无需改代码）
所有生成规则都在：
prompts/daily_diff.txt
prompts/weekly_summary.txt
可自由调整写作风格、结构、语言等。

❤️ 项目初衷
为了让读书会记录更加自动化、透明、轻松：
不需要手动整理阅读进度，也不需要编辑复杂的周报。
只需保持 ClickUp 更新 → 仓库会自动生成漂亮、自然的阅读记录。
