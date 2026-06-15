import re

EXPLAIN_RULES = [
    (r"^ls\b", "List directory contents"),
    (r"^ls\s+-la", "List all files with details including hidden files"),
    (r"^cd\b", "Change current directory"),
    (r"^pwd\b", "Print current working directory"),
    (r"^cat\b", "Display file contents"),
    (r"^grep\b", "Search text patterns in files or output"),
    (r"^find\b", "Search for files/directories matching criteria"),
    (r"^chmod\b", "Change file permissions"),
    (r"^chown\b", "Change file owner and group"),
    (r"^ps\b", "Show running processes"),
    (r"^kill\b", "Send signal to terminate a process"),
    (r"^kill\s+-9", "Force kill a process (cannot be ignored)"),
    (r"^docker\s+ps", "List Docker containers"),
    (r"^docker\s+logs", "View container logs"),
    (r"^docker\s+exec", "Run command inside a container"),
    (r"^kubectl\s+get", "List Kubernetes resources"),
    (r"^git\s+status", "Show working tree status"),
    (r"^git\s+add", "Stage files for commit"),
    (r"^git\s+commit", "Record changes to repository"),
    (r"^git\s+push", "Upload commits to remote repository"),
    (r"^git\s+pull", "Download and merge changes from remote"),
    (r"^git\s+clone", "Clone a remote repository"),
    (r"^git\s+checkout", "Switch branches or restore files"),
    (r"^git\s+merge", "Merge another branch into current branch"),
    (r"^git\s+reset\s+--hard", "Discard all local changes (destructive)"),
    (r"^git\s+rebase", "Reapply commits on top of another base"),
    (r"^git\s+stash", "Temporarily save uncommitted changes"),
    (r"^rm\s+-rf", "Recursively delete files/directories (destructive)"),
    (r"^rm\s+-rf\s+/", "Delete entire filesystem root (extremely dangerous)"),
    (r"^sudo\b", "Run command with superuser privileges"),
    (r"^curl\b", "Transfer data from/to a URL"),
    (r"^wget\b", "Download files from the web"),
    (r"^scp\b", "Securely copy files over SSH"),
    (r"^ssh\b", "Connect to remote host via SSH"),
    (r"^tar\b", "Archive or extract files"),
    (r"^systemctl\s+restart", "Restart a systemd service"),
    (r"^systemctl\s+status", "Check systemd service status"),
    (r"^df\b", "Show disk space usage"),
    (r"^du\b", "Show directory disk usage"),
    (r"^top\b", "Display real-time process activity"),
    (r"^htop\b", "Interactive process viewer"),
    (r"^ping\b", "Test network connectivity to a host"),
    (r"^netstat\b", "Display network connections and statistics"),
    (r"^ss\b", "Display socket statistics (modern netstat alternative)"),
    (r"^lsof\b", "List open files and ports"),
    (r"^crontab\b", "Manage scheduled tasks"),
    (r"^apt\s+install", "Install packages (Debian/Ubuntu)"),
    (r"^yum\s+install", "Install packages (RHEL/CentOS)"),
    (r"^brew\s+install", "Install packages (macOS Homebrew)"),
    (r"^pip\s+install", "Install Python packages"),
    (r"^npm\s+install", "Install Node.js packages"),
    (r"^mysql\b", "Connect to MySQL database"),
    (r"^redis-cli\b", "Connect to Redis CLI"),
    (r"^aws\b", "AWS CLI command"),
]

CHINESE_EXPLAIN = {
    "ls": "列出目录内容",
    "git status": "查看 Git 工作区状态",
    "git commit": "提交代码到本地仓库",
    "git push": "推送代码到远程仓库",
    "docker ps": "列出 Docker 容器",
    "rm -rf": "递归删除文件（危险操作）",
}


def explain_command(cmd):
    """Explain what a shell command does (local knowledge base)."""
    cmd = cmd.strip()
    if not cmd:
        return "Empty command"

    for pattern, explanation in EXPLAIN_RULES:
        if re.search(pattern, cmd, re.IGNORECASE):
            return explanation

    cmd_lower = cmd.lower()
    for key, explanation in CHINESE_EXPLAIN.items():
        if cmd_lower.startswith(key):
            return explanation

    parts = cmd.split()
    if parts:
        return f"Runs '{parts[0]}' — use 'man {parts[0]}' for full documentation"
    return "Unknown command"
