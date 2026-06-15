import re

DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+(/|\*|~|\$HOME)", "Recursive delete of root or home directory"),
    (r"rm\s+-rf\s+\S*\s+/(\s|$)", "Recursive delete targeting system paths"),
    (r"mkfs\.", "Filesystem format operation"),
    (r"dd\s+if=\S+\s+of=/dev/", "Direct disk write to device"),
    (r":\(\)\{\s*:\|:&\s*\};:", "Fork bomb"),
    (r">\s*/dev/sd[a-z]", "Direct write to block device"),
    (r"chmod\s+-R\s+777\s+/", "Recursive permission change on root"),
    (r"chown\s+-R\s+\S+\s+/", "Recursive ownership change on root"),
]

CAUTIOUS_PATTERNS = [
    (r"rm\s+-rf", "Recursive force delete"),
    (r"kill\s+-9", "Force kill process"),
    (r"systemctl\s+(stop|disable)", "Stop or disable system service"),
    (r"iptables\s+-F", "Flush firewall rules"),
    (r"docker\s+system\s+prune", "Remove unused Docker data"),
    (r"git\s+push\s+.*--force", "Force push to remote"),
    (r"git\s+reset\s+--hard", "Hard reset working tree"),
]


def classify_command(cmd):
    """Return 'dangerous', 'cautious', or 'safe' for a shell command."""
    if not cmd:
        return "safe"
    for pattern, _ in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return "dangerous"
    for pattern, _ in CAUTIOUS_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return "cautious"
    return "safe"


def get_warning_message(cmd):
    """Return a human-readable warning for a command, or None."""
    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return message
    for pattern, message in CAUTIOUS_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return message
    return None


def parse_ai_safety_label(text):
    """Extract safety label from AI response (last line: safe/cautious/dangerous)."""
    if not text:
        return "safe", text
    lines = text.strip().splitlines()
    if not lines:
        return "safe", text
    last = lines[-1].strip().lower()
    for label in ("dangerous", "cautious", "safe"):
        if label in last:
            body = "\n".join(lines[:-1]).strip() if len(lines) > 1 else text
            return label, body or text
    return "safe", text


def confirm_execution(cmd, level="dangerous"):
    """Ask user to confirm before executing a risky command."""
    label = "DANGEROUS" if level == "dangerous" else "CAUTION"
    print(f"\n⚠️  [{label}] The following command may cause data loss or system damage:")
    print(f"   {cmd}")
    try:
        answer = input("   Continue? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("y", "yes")
