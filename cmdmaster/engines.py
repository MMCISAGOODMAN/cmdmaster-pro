from cmdmaster.safety import classify_command
from cmdmaster.utils import platform_command

ERR = "\033[91m"
RES = "\033[0m"

COMPOUND_RULES = [
    (("docker", "log"), "docker logs -f <container>"),
    (("容器", "日志"), "docker logs -f <container>"),
    (("docker", "exec"), "docker exec -it <container> /bin/bash"),
    (("进入", "容器"), "docker exec -it <container> /bin/bash"),
    (("docker", "restart"), "docker restart <container>"),
    (("重启", "容器"), "docker restart <container>"),
    (("docker", "prune"), "docker system prune -af"),
    (("清理", "docker"), "docker system prune -af"),
    (("docker", "ps"), "docker ps -a"),
    (("容器", "状态"), "docker ps -a"),
    (("large", "file"), "find . -type f -size +100M -exec ls -lh {} \\;"),
    (("大文件",), "find . -type f -size +100M -exec ls -lh {} \\;"),
    (("clean", "log"), "find /var/log -name '*.log' -mtime +7 -delete"),
    (("清理", "日志"), "find /var/log -name '*.log' -mtime +7 -delete"),
]

LOCAL_RULES = [
    (["port", "端口", "端口占用"], "port"),
    (["disk usage", "top 10 disk", "磁盘使用"], "disk_usage"),
    (["disk space", "磁盘空间"], "disk_space"),
    (["memory", "mem", "内存", "内存使用"], "memory"),
    (["cpu", "cpu使用率", "处理器"], "cpu"),
    (["public ip", "公网ip", "外网ip"], "curl ifconfig.me"),
    (["scheduled", "crontab", "定时任务", "计划任务"], "crontab -l"),
    (["network latency", "网络延迟", "延迟"], "ping -c 4 8.8.8.8"),
    (["trace route", "路由追踪", "traceroute"], "traceroute 8.8.8.8"),
    (["system version", "系统版本"], "uname -a"),
    (["logged-in", "登录用户", "当前用户"], "w"),
    (["monitor", "实时监控", "系统监控"], "htop"),
    (["firewall", "防火墙", "开放端口"], "firewall"),
    (["process", "进程", "占用内存"], "process_list"),
    (["kubectl", "pod", "k8s"], "kubectl get pods -A"),
    (["nginx", "重启nginx"], "sudo systemctl restart nginx"),
    (["batch rename", "批量重命名"], "for f in *; do mv \"$f\" \"prefix_$f\"; done"),
    (["ssl", "certificate", "证书"], "echo | openssl s_client -connect <host>:443 2>/dev/null | openssl x509 -noout -dates"),
    (["redis", "redis状态"], "redis-cli ping"),
    (["mysql", "数据库连接"], "mysql -u <user> -p -h <host>"),
    (["aws", "s3"], "aws s3 ls"),
    (["journal", "系统日志"], "journalctl -xe --no-pager | tail -50"),
    (["nginx", "nginx状态"], "sudo systemctl status nginx"),
]

COMMAND_TEMPLATES = {
    "view": "cat <file path>",
    "查看": "cat <file path>",
    "create": "mkdir -p <directory name> && touch <file name>",
    "创建": "mkdir -p <directory name> && touch <file name>",
    "delete": "rm -rf <target>",
    "删除": "rm -rf <target>",
    "copy": "cp -r <source path> <destination path>",
    "复制": "cp -r <source path> <destination path>",
    "move": "mv <source path> <destination path>",
    "移动": "mv <source path> <destination path>",
    "find": "find <directory> -name '<file name>'",
    "查找": "find <directory> -name '<file name>'",
    "search": "grep -r '<keyword>' <directory>",
    "搜索": "grep -r '<keyword>' <directory>",
    "permissions": "chmod <permissions> <file>",
    "权限": "chmod <permissions> <file>",
    "owner": "chown <user>:<group> <file>",
    "process": "ps aux | grep <process name>",
    "进程": "ps aux | grep <process name>",
    "service": "systemctl status <service name>",
    "服务": "systemctl status <service name>",
    "network": "netstat -tlnp | grep <port>",
    "网络": "netstat -tlnp | grep <port>",
    "connection": "netstat -an | grep <port>",
    "bandwidth": "iftop -n -P",
    "monitor": "htop",
    "log": "tail -f <log file>",
    "日志": "tail -f <log file>",
    "compress": "tar -czf <archive name>.tar.gz <source file>",
    "压缩": "tar -czf <archive name>.tar.gz <source file>",
    "extract": "tar -xzf <archive name>.tar.gz",
    "解压": "tar -xzf <archive name>.tar.gz",
    "download": "wget <URL> or curl -O <URL>",
    "下载": "wget <URL> or curl -O <URL>",
    "upload": "scp <local file> <user>@<host>:<remote path>",
    "sync": "rsync -avz <source path> <destination path>",
    "system info": "uname -a",
    "disk space": "df -h",
    "磁盘空间": "df -h",
    "file size": "du -sh <directory>",
    "environment": "env | grep <variable name>",
    "user": "whoami or id",
    "group": "groups <user>",
    "install": "apt install <package name> or yum install <package name>",
    "安装": "apt install <package name> or yum install <package name>",
    "update": "apt update && apt upgrade or yum update",
    "更新": "apt update && apt upgrade or yum update",
    "uninstall": "apt remove <package name> or yum remove <package name>",
    "git": "git status",
    "submit": "git add . && git commit -m '<commit message>'",
    "commit": "git add . && git commit -m '<commit message>'",
    "提交": "git add . && git commit -m '<commit message>'",
    "push": "git push origin <branch name>",
    "推送": "git push origin <branch name>",
    "pull": "git pull origin <branch name>",
    "拉取": "git pull origin <branch name>",
    "branch": "git branch or git branch -a",
    "分支": "git branch or git branch -a",
    "create branch": "git branch <branch name>",
    "创建分支": "git branch <branch name>",
    "switch": "git checkout <branch name>",
    "switch branch": "git checkout <branch name>",
    "切换分支": "git checkout <branch name>",
    "merge": "git merge <branch name>",
    "合并": "git merge <branch name>",
    "status": "git status",
    "状态": "git status",
    "clone": "git clone <repository url>",
    "克隆": "git clone <repository url>",
    "add": "git add <file name>",
    "stage": "git add <file name>",
    "reset": "git reset <file name>",
    "diff": "git diff",
    "difference": "git diff",
    "stash": "git stash",
    "tag": "git tag -a <tag name> -m '<description>'",
    "标签": "git tag -a <tag name> -m '<description>'",
    "remote": "git remote -v",
    "远程": "git remote -v",
    "init": "git init",
    "初始化": "git init",
    "rebase": "git rebase <branch name>",
    "变基": "git rebase <branch name>",
    "cherry-pick": "git cherry-pick <commit hash>",
    "撤销": "git checkout -- <file>",
    "undo": "git checkout -- <file>",
}

PRIORITY_KEYWORDS = [
    "commit", "submit", "提交", "push", "推送", "pull", "拉取",
    "clone", "克隆", "branch", "分支", "switch", "切换分支",
    "merge", "合并", "status", "状态", "log", "日志", "tag", "标签",
    "remote", "远程", "init", "初始化", "rebase", "变基", "cherry-pick",
    "撤销", "undo",
]

_PLATFORM_KEYS = {"port", "disk_usage", "disk_space", "memory", "cpu", "firewall", "process_list"}


def _resolve_command(command_or_key):
    if command_or_key in _PLATFORM_KEYS:
        return platform_command(command_or_key)
    return command_or_key


def local_engine(prompt):
    p = prompt.lower()

    if classify_command(prompt) == "dangerous":
        return f"{ERR}❌ Dangerous operation blocked{RES}"

    for keywords, command in COMPOUND_RULES:
        if all(kw.lower() in p or kw in prompt for kw in keywords):
            return command

    for keywords, command in LOCAL_RULES:
        for kw in keywords:
            if kw.lower() in p or kw in prompt:
                return _resolve_command(command)

    return None


def local_ai_engine(prompt):
    """Provide command suggestions when cloud AI is unavailable."""
    p = prompt.lower()

    for keyword in PRIORITY_KEYWORDS:
        if keyword.lower() in p or keyword in prompt:
            return COMMAND_TEMPLATES.get(keyword, f"# Please refer to: {keyword}")

    for keyword, command in COMMAND_TEMPLATES.items():
        if keyword not in PRIORITY_KEYWORDS and (keyword.lower() in p or keyword in prompt):
            return command

    return (
        "Please try more specific descriptions, e.g.: check port, create file, find process\n"
        "或使用更具体的描述，例如：查看端口、创建文件、查找进程"
    )
