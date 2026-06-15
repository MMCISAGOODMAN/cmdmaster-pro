import json
import os

from cmdmaster.config import get_config_dir

TEMPLATES_FILE = os.path.join(get_config_dir(), "templates.json")


def load_user_templates():
    if not os.path.exists(TEMPLATES_FILE):
        return {}
    try:
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def match_user_template(prompt):
    """Match prompt against user-defined templates (exact or keyword)."""
    templates = load_user_templates()
    if not templates:
        return None

    p_lower = prompt.lower().strip()
    if p_lower in {k.lower() for k in templates}:
        for key, cmd in templates.items():
            if key.lower() == p_lower:
                return cmd

    for key, cmd in templates.items():
        k_lower = key.lower()
        if k_lower in p_lower or p_lower in k_lower:
            return cmd
    return None


def save_user_template(key, command):
    templates = load_user_templates()
    templates[key] = command
    template_dir = os.path.dirname(TEMPLATES_FILE)
    try:
        if template_dir:
            os.makedirs(template_dir, exist_ok=True)
        with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def remove_user_template(key):
    templates = load_user_templates()
    removed = None
    for k in list(templates.keys()):
        if k.lower() == key.lower():
            removed = templates.pop(k)
            break
    if removed is None:
        return False
    try:
        with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def list_user_templates():
    return load_user_templates()
