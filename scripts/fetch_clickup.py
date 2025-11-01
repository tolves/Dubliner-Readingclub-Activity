import os
import requests
import json

TOKEN = os.environ.get("CLICKUP_TOKEN")
SPACE_ID = "90157555812"   # ← 你的 space_id

def main():
    if not TOKEN:
        print("❌ CLICKUP_TOKEN not found")
        return

    headers = {"Authorization": TOKEN}

    # 第一步：获取 space 下的 list
    list_url = f"https://api.clickup.com/api/v2/space/{SPACE_ID}/list"
    print(f"🚀 Fetching lists from space {SPACE_ID}")
    r = requests.get(list_url, headers=headers)
    print("HTTP status:", r.status_code)
    if r.status_code != 200:
        print("❌ Error:", r.text)
        return

    lists = r.json().get("lists", [])
    print(f"✅ Found {len(lists)} lists")
    if not lists:
        print("⚠️  No lists found in this space.")
        return

    all_tasks = []

    # 第二步：遍历 list 拉取任务
    for lst in lists:
        list_id = lst["id"]
        list_name = lst["name"]
        print(f"\n➡️  Getting tasks from list '{list_name}' ({list_id})")

        task_url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
        resp = requests.get(task_url, headers=headers)
        print("   HTTP status:", resp.status_code)

        if resp.status_code != 200:
            print("   ❌ Error:", resp.text)
            continue

        tasks = resp.json().get("tasks", [])
        print(f"   ✅ Found {len(tasks)} tasks")
        all_tasks.extend(tasks)

    # 保存结果
    os.makedirs("data", exist_ok=True)
    filename = "data/tasks_list.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved {len(all_tasks)} tasks to {filename}")

if __name__ == "__main__":
    main()
