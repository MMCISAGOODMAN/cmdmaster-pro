import json
import os

from cmdmaster.favorites import load_favorites

HIST_FILE = os.path.expanduser("~/.cmdmaster-pro.history")

SUGGESTION_POOL = [
    "check port usage",
    "top 10 disk usage",
    "check CPU usage",
    "check memory usage",
    "check public IP",
    "check scheduled tasks",
    "clean logs older than 7 days",
    "view Docker container logs",
    "enter Docker container",
    "restart Docker container",
    "open firewall port",
    "check network latency",
    "trace route",
    "check system version",
    "check current logged-in users",
    "real-time system monitoring",
    "check SSL certificate expiry",
    "restart nginx service",
    "查看CPU使用率",
    "查看磁盘空间",
    "查看端口占用",
    "commit提交代码",
    "push代码到远程",
    "查看docker容器状态",
    "清理docker无用镜像",
]


def load_history():
    if not os.path.exists(HIST_FILE):
        return []
    try:
        with open(HIST_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError:
        return []


def save_history(prompt):
    if len(prompt) < 2:
        return
    history = load_history()
    if prompt in history:
        history.remove(prompt)
    history.insert(0, prompt)
    history = history[:30]
    try:
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(history) + "\n")
    except OSError:
        pass


def clear_history():
    try:
        os.remove(HIST_FILE)
        return True
    except OSError:
        return False


def get_smart_suggestions(input_text, limit=4):
    text = input_text.lower().strip()
    matches = []
    for source in (load_history(), load_favorites(), SUGGESTION_POOL):
        for item in source:
            if text in item.lower() and item not in matches:
                matches.append(item)
    return matches[:limit]


def search_history(query, limit=10):
    q = query.lower().strip()
    if not q:
        return load_history()[:limit]
    return [h for h in load_history() if q in h.lower()][:limit]


def export_history(path):
    data = {
        "history": load_history(),
        "favorites": load_favorites(),
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def import_history(path, merge=True):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False

    imported = data.get("history", [])
    if not isinstance(imported, list):
        return False

    if merge:
        current = load_history()
        merged = []
        for item in imported + current:
            if item and item not in merged:
                merged.append(item)
        merged = merged[:30]
    else:
        merged = [h for h in imported if h][:30]

    try:
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(merged) + "\n")
        return True
    except OSError:
        return False
