import os
import json
import datetime
import requests

# === 环境变量与常量 ===
TOKEN = os.environ.get("CLICKUP_TOKEN")
SPACE_ID = "90157555812"   # 你的空间 ID

def log(msg):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def fetch_lists(space_id, headers):
    """获取 space 下的所有 list"""
    url = f"https://api.clickup.com/api/v2/space/{space_id}/list"
    log(f"➡️  Fetching lists from space {space_id}")
    r = requests.get(url, headers=headers, timeout=30)
    log(f"   HTTP {r.status_code}")
    if r.status_code != 200:
        log(f"   ❌ Error: {r.text}")
        return []
    return r.json().get("lists", [])

def fetch_tasks_from_list(list_id, headers):
    """获取单个 list 下的所有任务"""
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        log(f"   ❌ List {list_id} fetch failed: {r.text[:200]}")
        return []
    data = r.json()
    return data.get("tasks", [])

def main():
    log("🚀 Start fetching tasks from ClickUp")

    if not TOKEN:
        log("❌ Missing CLICKUP_TOKEN in environment variables")
        return

    headers = {"Authorization": TOKEN}
    all_tasks = []

    # === Step 1: 获取该 Space 下的所有 List ===
    lists = fetch_lists(SPACE_ID, headers)
    log(f"✅ Found {len(lists)} lists")

    # === Step 2: 遍历每个 List 获取任务 ===
    for lst in lists:
        list_id = lst["id"]
        list_name = lst["name"]
        log(f"➡️  Fetching tasks from list: {list_name} ({list_id})")

        tasks = fetch_tasks_from_list(list_id, headers)
        log(f"   ✅ Got {len(tasks)} tasks")

        all_tasks.extend(tasks)

    # === Step 3: 保存结果 ===
    os.makedirs("data", exist_ok=True)
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"data/{date_str}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)

    log(f"💾 Saved {len(all_tasks)} tasks to {filename}")

    # 打印前几条任务预览
    if all_tasks:
        preview = all_tasks[:3]
        log("🔍 Preview of first few tasks:")
        print(json.dumps(preview, ensure_ascii=False, indent=2)[:500])

    log("🎯 Done.")

if __name__ == "__main__":
    main()
