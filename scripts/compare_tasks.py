import json
import os
import datetime

def log(msg):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def load_json(filepath):
    if not os.path.exists(filepath):
        log(f"⚠️  File not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def task_summary(task):
    """提取任务的主要信息"""
    return {
        "id": task.get("id"),
        "name": task.get("name"),
        "status": task.get("status", {}).get("status"),
        "assignees": [a.get("username") for a in task.get("assignees", [])],
        "date_updated": task.get("date_updated")
    }

def compare_tasks(yesterday, today):
    """比对两天任务变化"""
    yesterday_map = {t["id"]: task_summary(t) for t in yesterday}
    today_map = {t["id"]: task_summary(t) for t in today}

    added, removed, changed, completed = [], [], [], []

    for tid, t in today_map.items():
        if tid not in yesterday_map:
            added.append(t)
        else:
            old = yesterday_map[tid]
            if t["status"] != old["status"]:
                changed.append({"id": tid, "name": t["name"], "from": old["status"], "to": t["status"]})
            if t["status"] in ["complete", "closed", "done"] and old["status"] not in ["complete", "closed", "done"]:
                completed.append(t)

    for tid, t in yesterday_map.items():
        if tid not in today_map:
            removed.append(t)

    return added, removed, changed, completed

def generate_markdown_report(date_str, added, removed, changed, completed):
    """生成 Markdown 报告"""
    lines = [f"# 📅 ClickUp 活动摘要 - {date_str}", ""]

    if added:
        lines.append("## 🆕 新增任务")
        for t in added:
            lines.append(f"- {t['name']}  _(负责人: {', '.join(t['assignees']) or '无'})_")
        lines.append("")

    if completed:
        lines.append("## ✅ 完成任务")
        for t in completed:
            lines.append(f"- {t['name']}")
        lines.append("")

    if changed:
        lines.append("## 🔄 状态变更")
        for c in changed:
            lines.append(f"- {c['name']}: {c['from']} → {c['to']}")
        lines.append("")

    if removed:
        lines.append("## ❌ 删除任务")
        for t in removed:
            lines.append(f"- {t['name']}")
        lines.append("")

    if not (added or removed or changed or completed):
        lines.append("✨ 没有变化，一切保持稳定。")

    return "\n".join(lines)

def main():
    log("🚀 Start comparing tasks")

    # 文件路径
    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    yesterday_str = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    today_file = f"data/{today_str}.json"
    yesterday_file = f"data/{yesterday_str}.json"

    today_tasks = load_json(today_file)
    yesterday_tasks = load_json(yesterday_file)

    if not today_tasks or not yesterday_tasks:
        log("⚠️  没有足够的数据进行对比。")
        return

    added, removed, changed, completed = compare_tasks(yesterday_tasks, today_tasks)

    log(f"🆕 新增任务: {len(added)}")
    log(f"✅ 完成任务: {len(completed)}")
    log(f"🔄 状态变更: {len(changed)}")
    log(f"❌ 删除任务: {len(removed)}")

    # 输出预览
    if added:
        log(f"▶️  新增任务示例: {added[0]['name']}")
    if changed:
        log(f"▶️  状态变更示例: {changed[0]['name']} ({changed[0]['from']} → {changed[0]['to']})")

    # 生成 Markdown
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/{today_str}.md"
    md = generate_markdown_report(today_str, added, removed, changed, completed)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    log(f"💾 Report saved to {report_path}")
    log("🎯 Done.")

if __name__ == "__main__":
    main()
