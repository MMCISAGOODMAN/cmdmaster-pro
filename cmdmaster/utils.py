import re
import subprocess
import sys


def get_platform():
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    return "other"


def platform_command(key):
    """Return platform-specific shell command for a known key."""
    linux = {
        "cpu": "top -bn1 | grep Cpu",
        "memory": "free -h",
        "disk_usage": "du -sh /* 2>/dev/null | sort -rh | head -10",
        "disk_space": "df -h",
        "port": "ss -tlnp | grep :<port>",
        "process_list": "ps aux --sort=-%mem | head -10",
        "firewall": "sudo ufw allow <port>/tcp",
    }
    macos = {
        "cpu": "top -l 1 | grep CPU",
        "memory": "vm_stat",
        "disk_usage": "du -sh /* 2>/dev/null | sort -rh | head -10",
        "disk_space": "df -h",
        "port": "lsof -i :<port> | grep LISTEN",
        "process_list": "ps aux -r | head -10",
        "firewall": "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add <app>",
    }
    platform = get_platform()
    table = macos if platform == "macos" else linux
    return table.get(key, linux.get(key))


def extract_shell_commands(text):
    """Extract executable shell commands from generated output."""
    if not text:
        return []
    commands = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("```"):
            continue
        lower = line.lower()
        if lower in ("safe", "cautious", "dangerous"):
            continue
        if lower.startswith(("safe", "cautious", "dangerous")) and len(line) < 20:
            continue
        # Skip pure explanation lines
        if re.match(r"^(说明|解释|note|explanation|please|try|使用|run this)", line, re.I):
            continue
        if line.endswith(":") and not re.search(r"[|;&$`]", line):
            continue
        commands.append(line)
    return commands


def primary_command(text):
    """Return the first executable command from generated output."""
    commands = extract_shell_commands(text)
    return commands[0] if commands else text.strip()


def copy_to_clipboard(text):
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        if sys.platform.startswith("linux"):
            for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    subprocess.run(cmd, input=text, text=True, check=True)
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
    except (subprocess.CalledProcessError, OSError):
        pass
    return False
