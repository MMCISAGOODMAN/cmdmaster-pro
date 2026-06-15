import os

FAV_FILE = os.path.expanduser("~/.cmdmaster-pro.favorites")
MAX_FAVORITES = 50


def load_favorites():
    if not os.path.exists(FAV_FILE):
        return []
    try:
        with open(FAV_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError:
        return []


def add_favorite(prompt):
    if len(prompt) < 2:
        return False
    favorites = load_favorites()
    if prompt in favorites:
        favorites.remove(prompt)
    favorites.insert(0, prompt)
    favorites = favorites[:MAX_FAVORITES]
    try:
        with open(FAV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(favorites) + "\n")
        return True
    except OSError:
        return False


def remove_favorite(prompt):
    favorites = load_favorites()
    if prompt not in favorites:
        return False
    favorites.remove(prompt)
    try:
        with open(FAV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(favorites) + ("\n" if favorites else ""))
        return True
    except OSError:
        return False


def list_favorites():
    return load_favorites()
