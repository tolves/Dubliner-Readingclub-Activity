# 📚 Dubliner Reading Club Activity  
自动生成 **每日阅读进度报告** & **每周读书会周报**

---

## ✨ 功能概览

- ✅ **每日阅读变化对比（Daily Diff）**  
  自动比较前一天与当天的 ClickUp JSON，生成自然语言阅读进度报告。

- ✅ **每周总结（Weekly Summary）**  
  汇总过去 7 天的变化，自动生成结构化、自然语言的周报。

- ✅ **GitHub Actions 自动化**  
  每周一定时执行脚本，生成 daily / weekly 报告并自动 push。

- ✅ **Prompt 模板可独立编辑**  
  所有规则存放于 `prompts/`，可自由调整语气、结构，无需修改代码。

---

## 🚀 本地运行

```bash
pip install openai
export OPENAI_API_KEY="你的 key"
python scripts/weekly_summary.py
```

生成文件：

- ✅ **reports/YYYY-MM-DD_daily_report.md**

- ✅ **weekly/YYYY-Wxx.md**

---

## 🤖 GitHub Actions

自动生成：

- ✅ 每日报告（daily diff）

- ✅ 每周周报

- ✅ 分开提交 daily / weekly

---

## ✏️ Prompt 可编辑

- ✅ 无需修改 Python 代码，只需编辑：

```
prompts/daily_diff.txt

prompts/weekly_summary.txt
```

- ✅ 即可改变报告风格。

---

❤️ 关于项目

本项目旨在让读书会记录更加轻松透明：

只需更新 ClickUp，即可自动生成每日/每周的清晰阅读记录与总结。
