import os
import sys

_enabled = None


def colors_enabled():
    global _enabled
    if _enabled is not None:
        return _enabled
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("CMDMASTER_FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def set_colors(enabled):
    global _enabled
    _enabled = enabled


def c(code, text):
    if colors_enabled():
        return f"\033[{code}m{text}\033[0m"
    return text


PRI = lambda t: c("94", t)
ACC = lambda t: c("92", t)
WAR = lambda t: c("93", t)
CMD = lambda t: c("96", t)
ERR = lambda t: c("91", t)
DIM = lambda t: c("90", t)
