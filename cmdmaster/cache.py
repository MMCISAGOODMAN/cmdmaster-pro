import json
import os
import time

from cmdmaster.config import get_config_dir

CACHE_FILE = os.path.join(get_config_dir(), "cache.json")
CACHE_TTL = 86400  # 24 hours
MAX_CACHE_ENTRIES = 100


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(data):
    cache_dir = os.path.dirname(CACHE_FILE)
    try:
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get_cached(prompt):
    key = prompt.strip().lower()
    entry = _load_cache().get(key)
    if not entry:
        return None
    if time.time() - entry.get("ts", 0) > CACHE_TTL:
        return None
    return entry


def set_cached(prompt, result, source="local"):
    key = prompt.strip().lower()
    cache = _load_cache()
    cache[key] = {
        "result": result,
        "source": source,
        "ts": time.time(),
    }
    if len(cache) > MAX_CACHE_ENTRIES:
        sorted_keys = sorted(cache, key=lambda k: cache[k].get("ts", 0))
        for old_key in sorted_keys[: len(cache) - MAX_CACHE_ENTRIES]:
            cache.pop(old_key, None)
    _save_cache(cache)


def clear_cache():
    try:
        os.remove(CACHE_FILE)
        return True
    except OSError:
        return False
