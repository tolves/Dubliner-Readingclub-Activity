# 📚 Dubliner ReadingClub Activity Tracker

[![Daily Report Workflow](https://github.com/<你的GitHub用户名>/dubliner-readingclub-activity/actions/workflows/daily-report.yml/badge.svg)](https://github.com/<你的GitHub用户名>/dubliner-readingclub-activity/actions)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Automation-Daily%20at%207AM%20Dublin-orange)

> ✨ **Dubliner ReadingClub Activity Tracker**  
> 自动从 ClickUp 获取读书会任务数据，分析每日变化，生成 Markdown 报告，并通过 GitHub Actions 自动更新。

---

## 🧩 功能概览

| 功能 | 描述 |
|------|------|
| 🕐 **每日自动运行** | GitHub Actions 每天都柏林时间早上 7 点执行 |
| 🧾 **任务快照保存** | 从 ClickUp 拉取任务数据，保存为 `data/YYYY-MM-DD.json` |
| 🔍 **自动差异分析** | 比较昨天与今天的任务变化（新增、完成、状态变更、删除） |
| 🪄 **Markdown 报告生成** | 自动生成每日摘要到 `reports/YYYY-MM-DD.md` |
| 🚀 **自动提交结果** | 报告自动 push 回 GitHub 仓库 |

---

## 🚀 使用方法

### 🧭 手动运行
在 GitHub 仓库的 **Actions** 标签页中：
1. 找到工作流 **Daily ClickUp Task Report**
2. 点击 **Run workflow** 手动触发一次

### 🕐 自动运行
工作流会根据 `daily-report.yml` 中的 cron 表达式自动执行：
0 1 * * * # 每天都柏林时间早上1点

---

## 🧠 输出示例

生成的 Markdown 报告（位于 `reports/YYYY-MM-DD.md`）：

```markdown
# 📅 ClickUp 活动摘要 - 2025-11-02

## 🆕 新增任务
- 《1984》读后讨论 _(负责人: Alice)_

## ✅ 完成任务
- 读书会报名表发布

## 🔄 状态变更
- 场地确认: in progress → done

```

🧮 自动化工作流说明

工作流文件路径：

.github/workflows/daily-report.yml


执行流程：

1. 每天早上 1 点（Europe/Dublin 时区）运行
2. 调用 ClickUp API 获取任务
3. 比较前后快照差异
4. 生成 Markdown 报告
5. 自动提交结果回仓库

🧩 后续扩展计划

1. 统计任务状态分布（To Do / In Progress / Done）
2. 生成周报 / 月报
3. 使用 ChatGPT 自动生成自然语言总结
4. 将报告自动发布到 Slack / 邮箱 / Notion
