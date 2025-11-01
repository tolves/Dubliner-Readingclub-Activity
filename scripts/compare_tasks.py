import os
import json
import datetime as dt
from pathlib import Path

# 🔧 确保脚本在项目根目录运行
os.chdir(Path(__file__).resolve().parent.parent)


def log(msg):
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# === 工具函数 ===
def get_username(obj):
    """从 ClickUp 对象中提取用户名"""
    if not obj:
        return None
    if isinstance(obj, dict):
        return obj.get("username") or obj.get("name")
    return str(obj)


def extract_checklist_items(task):
    """提取 checklist（阅读章节）信息：name -> {'resolved': bool, 'by': username}"""
    items = {}
    for checklist in task.get("checklists", []):
        checklist_name = checklist.get("name") or "读书小组"
        for it in checklist.get("items", []):
            name = it.get("name")
            resolved = it.get("resolved", False)
            if isinstance(resolved, (int, str)):
                resolved = str(resolved).lower() in ("1", "true", "yes")

            # 优先用子项 assignee/creator；若都没有，则用 checklist 名称
            user = (
                get_username(it.get("assignee"))
                or get_username(it.get("creator"))
                or checklist_name
            )

            if name:
                items[name] = {"resolved": bool(resolved), "by": user}
    return items


def summarize_task(task):
    """提取任务主要字段及负责人信息"""
    assignees = task.get("assignees") or []
    checklists = task.get("checklists") or []
    updated_by = get_username(task.get("updated_by"))
    if not updated_by and assignees:
        updated_by = get_username(assignees[0])
    elif not updated_by and checklists:
        updated_by = checklists[0].get("name")

    return {
        "id": task.get("id"),
        "name": task.get("name"),
        "status": task.get("status", {}).get("status"),
        "creator": get_username(task.get("creator")),
        "updated_by": updated_by,
        "checklist": extract_checklist_items(task)
    }


# === 核心比较逻辑 ===
def compare_tasks(yesterday, today):
    """返回五类变化：新增任务、删除任务、状态变化、完成任务、读书进度变化"""
    ymap = {t["id"]: summarize_task(t) for t in yesterday}
    tmap = {t["id"]: summarize_task(t) for t in today}

    added, removed, changed, completed, progress_updates = [], [], [], [], []

    for tid, t in tmap.items():
        if tid not in ymap:
            added.append(t)
            continue

        old = ymap[tid]

        # 状态变化
        if t["status"] != old["status"]:
            changed.append({
                "id": tid,
                "name": t["name"],
                "from": old["status"],
                "to": t["status"],
                "by": t["updated_by"]
            })

        # 完成任务
        if t["status"] in ["complete", "closed", "done"] and old["status"] not in ["complete", "closed", "done"]:
            completed.append(t)

        # 读书进度对比
        old_items, new_items = old["checklist"], t["checklist"]
        diffs = []

        for name, info in new_items.items():
            val, user = info["resolved"], info["by"]
            if name not in old_items:
                who = f"（由 {user} 添加）" if user else ""
                diffs.append(f"🆕 新增阅读章节：{name} {'✅' if val else '⬜️'}{who}")
            elif old_items[name]["resolved"] != val:
                if val:
                    who = f"（{user or '未知成员'} 已读完）"
                    diffs.append(f"✅ 已读完章节：{name} {who}")
                else:
                    who = f"（{user or '未知成员'} 标记未读）"
                    diffs.append(f"⬜️ 标记未读章节：{name} {who}")

        for name in old_items:
            if name not in new_items:
                diffs.append(f"❌ 移除章节：{name}")

        if diffs:
            progress_updates.append({
                "id": tid,
                "name": t["name"],
                "diffs": diffs
            })

    # 删除任务
    for tid, t in ymap.items():
        if tid not in tmap:
            removed.append(t)

    return added, removed, changed, completed, progress_updates


# === 报告输出 ===
def generate_markdown(date_str, added, removed, changed, completed, progress_updates):
    """生成 Markdown 报告"""
    lines = [f"# 📅 Dubliner读书会 每日阅读报告 - {date_str}", ""]

    if added:
        lines.append("## 🆕 新增书籍任务")
        for t in added:
            who = f"（由 {t.get('creator') or '未知'} 创建）"
            lines.append(f"- **{t['name']}** {who}")
        lines.append("")

    if completed:
        lines.append("## ✅ 已完成书籍")
        for t in completed:
            who = f"（由 {t.get('updated_by') or '未知'} 完成）"
            lines.append(f"- **{t['name']}** {who}")
        lines.append("")

    if changed:
        lines.append("## 🔄 阅读状态变化")
        for c in changed:
            who = f"（{c['by'] or '未知'} 更新）"
            lines.append(f"- **{c['name']}**：{c['from']} → {c['to']} {who}")
        lines.append("")

    if progress_updates:
        lines.append("## 📚 读书进度")
        for c in progress_updates:
            lines.append(f"- **{c['name']}**")
            for d in c["diffs"]:
                lines.append(f"  - {d}")
        lines.append("")
        lines.append(f"📖 今日共有 {len(progress_updates)} 本书更新了阅读进度。继续保持！")
        lines.append("")

    if removed:
        lines.append("## 🗑️ 删除书籍任务")
        for t in removed:
            lines.append(f"- {t['name']}")
        lines.append("")

    if len(lines) <= 2:
        lines.append("今天没有检测到任何书籍或阅读进度变化。")

    return "\n".join(lines)


# === 主入口 ===
def main():
    data_dir = "data"
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    today_str, yesterday_str = today.isoformat(), yesterday.isoformat()

    yfile = os.path.join(data_dir, f"{yesterday_str}.json")
    tfile = os.path.join(data_dir, f"{today_str}.json")

    log(f"📖 对比任务文件：{yfile} → {tfile}")

    if not os.path.exists(yfile) or not os.path.exists(tfile):
        log("❌ 缺少数据文件，无法生成报告。")
        return

    with open(yfile, "r", encoding="utf-8") as fy:
        yesterday_tasks = json.load(fy)
    with open(tfile, "r", encoding="utf-8") as ft:
        today_tasks = json.load(ft)

    added, removed, changed, completed, progress_updates = compare_tasks(yesterday_tasks, today_tasks)
    report = generate_markdown(today_str, added, removed, changed, completed, progress_updates)

    os.makedirs("reports", exist_ok=True)
    out_path = os.path.join("reports", f"{today_str}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    log(f"✅ 报告已生成：{out_path}")


if __name__ == "__main__":
    main()
