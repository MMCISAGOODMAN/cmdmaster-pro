#!/usr/bin/env python3
import sys, os, json, hashlib, requests, platform

# Try to load custom AI configuration
try:
    from ai_config import AI_URL, AI_TOKEN, AI_MODEL
except ImportError:
    # Use default configuration
    AI_URL = None
    AI_TOKEN = None
    AI_MODEL = None

# --------------------
# Advanced Topics
# --------------------
PRI = '\033[94m'
ACC = '\033[92m'
WAR = '\033[93m'
CMD = '\033[96m'
ERR = '\033[91m'
DIM = '\033[90m'
RES = '\033[0m'

# --------------------
# AI Configuration
# --------------------
# If configuration not loaded from ai_config.py, use default values
if AI_URL is None:
    AI_URL = "https://api.chatanywhere.tech/chat/completions"  # VolcEngine API
if AI_TOKEN is None:
    AI_TOKEN = "sk-Fat40iO2E1f7QyV9Sj9Drx9m2NlTmba911ITJ5aFPbAD2ejh"  # Default API Token
if AI_MODEL is None:
    AI_MODEL = "gpt-3.5-turbo"  # Default model name

# --------------------
# Configuration File
# --------------------
HIST_FILE = os.path.expanduser("~/.cmdmaster-pro.history")

# ==============================================
# Built-in Industry Library
# ==============================================
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
]

# ==============================================
# History Management
# ==============================================
def load_history():
    if not os.path.exists(HIST_FILE):
        return []
    try:
        with open(HIST_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except:
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
        with open(HIST_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(history) + '\n')
    except:
        pass

def clear_history():
    try:
        os.remove(HIST_FILE)
        print(f"\n{ACC}✅ History cleared{RES}\n")
    except:
        print(f"\n{ERR}❌ Clear failed{RES}\n")

def show_history():
    history = load_history()
    if not history:
        print(f"\n{DIM}No history records{RES}\n")
        return
    print(f"\n{WAR}📜 History (last 30 entries){RES}")
    for i, line in enumerate(history, 1):
        print(f"{ACC}{i:2d}.{RES} {line}")
    print()

# ==============================================
# Smart Completion: History + Built-in Library
# ==============================================
def get_smart_suggestions(input_text):
    text = input_text.lower().strip()
    history = load_history()
    matches = []
    for h in history:
        if text in h.lower() and h not in matches:
            matches.append(h)
    for s in SUGGESTION_POOL:
        if text in s.lower() and s not in matches:
            matches.append(s)
    return matches[:4]

def show_suggestions(input_text):
    suggestions = get_smart_suggestions(input_text)
    if not suggestions:
        return
    print(f"{WAR}💡 Smart completion (history + recommendations):{RES}")
    for s in suggestions:
        print(f"  {ACC}→{RES} {s}")

# ==============================================
# Local Expert Engine
# ==============================================
def local_engine(prompt):
    p = prompt.lower()
    if "port" in p:
        return "lsof -i :<port number> | grep LISTEN"
    if "disk" in p:
        return "du -sh /* | sort -rh | head -10"
    if "memory" in p or "mem" in p:
        return "free -h"
    if "cpu" in p:
        return "top -bn1 | grep Cpu"
    if "public ip" in p:
        return "curl ifconfig.me"
    if "docker" in p and "log" in p:
        return "docker logs -f <container>"
    if "scheduled" in p or "crontab" in p:
        return "crontab -l"
    if "rm" in p and "/" in p:
        return f"{ERR}❌ Dangerous operation blocked{RES}"
    return None

def local_ai_engine(prompt):
    """Local AI engine that provides basic command suggestions when cloud is unavailable"""
    p = prompt.lower()

    # Basic command mapping
    command_templates = {
        "view": "cat <file path>",
        "create": "mkdir -p <directory name> && touch <file name>",
        "delete": "rm -rf <target>",
        "copy": "cp -r <source path> <destination path>",
        "move": "mv <source path> <destination path>",
        "find": "find <directory> -name '<file name>'",
        "search": "grep -r '<keyword>' <directory>",
        "permissions": "chmod <permissions> <file>",
        "owner": "chown <user>:<group> <file>",
        "process": "ps aux | grep <process name>",
        "service": "systemctl status <service name>",
        "network": "netstat -tlnp | grep <port>",
        "connection": "netstat -an | grep <port>",
        "bandwidth": "iftop -n -P",
        "monitor": "htop",
        "log": "tail -f <log file>",
        "compress": "tar -czf <archive name>.tar.gz <source file>",
        "extract": "tar -xzf <archive name>.tar.gz",
        "download": "wget <URL> or curl -O <URL>",
        "upload": "scp <local file> <user>@<host>:<remote path>",
        "sync": "rsync -avz <source path> <destination path>",
        "system info": "uname -a",
        "disk space": "df -h",
        "file size": "du -sh <directory>",
        "environment": "env | grep <variable name>",
        "user": "whoami or id",
        "group": "groups <user>",
        "install": "apt install <package name> or yum install <package name>",
        "update": "apt update && apt upgrade or yum update",
        "uninstall": "apt remove <package name> or yum remove <package name>",
        # Git related commands
        "git": "git status",
        "submit": "git add . && git commit -m '<commit message>'",
        "commit": "git add . && git commit -m '<commit message>'",
        "push": "git push origin <branch name>",
        "push": "git push origin <branch name>",
        "pull": "git pull origin <branch name>",
        "pull": "git pull origin <branch name>",
        "branch": "git branch or git branch -a",
        "create branch": "git branch <branch name>",
        "switch": "git checkout <branch name>",
        "switch branch": "git checkout <branch name>",
        "merge": "git merge <branch name>",
        "status": "git status",
        "log": "git log --oneline",
        "clone": "git clone <repository url>",
        "clone": "git clone <repository url>",
        "add": "git add <file name>",
        "stage": "git add <file name>",
        "reset": "git reset <file name>",
        "reset": "git reset <file name>",
        "diff": "git diff",
        "difference": "git diff",
        "stash": "git stash",
        "stash": "git stash",
        "tag": "git tag or git tag -a <tag name> -m '<description>'",
        "tag": "git tag",
        "remote": "git remote -v",
        "remote": "git remote -v",
        "init": "git init",
        "init": "git init",
    }

    # Find matching commands (sorted by priority)
    # First check more specific keywords
    priority_keywords = ['commit', 'submit', 'push', 'push', 'pull', 'pull', 'clone', 'clone', 'branch', 'switch', 'merge', 'status', 'log', 'tag', 'remote', 'init']

    for keyword in priority_keywords:
        if keyword in p:
            return command_templates.get(keyword, f"# Please refer to: {keyword}")

    # Then check other keywords
    for keyword, command in command_templates.items():
        if keyword in p and keyword not in priority_keywords:
            return command

    # If no match, return general suggestion
    return "Please try more specific command descriptions, such as: check port, create file, find process, etc."

# ==============================================
# Network Requests
# ==============================================

def api(action, **kwargs):
    if action == "ai":
        # Directly call large model API
        prompt = kwargs.get("prompt", "")
        try:
            headers = {
                "Authorization": f"Bearer {AI_TOKEN}",
                "Content-Type": "application/json"
            }

            # Determine which API format to use based on URL
            if "ark.cn-beijing.volces.com" in AI_URL:
                # VolcEngine format
                data = {
                    "model": AI_MODEL,
                    "input": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            else:
                # OpenAI/DeepSeek compatible format
                data = {
                    "model": AI_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a shell command assistant. Only return commands and brief explanations, don't use markdown, maximum 2 commands, mark the last line as safe / cautious / dangerous"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 300
                }

            print(f"{AI_URL}AI address")
            response = requests.post(AI_URL, json=data, headers=headers, timeout=15)
            result = response.json()

            # Handle response based on different API formats
            if "ark.cn-beijing.volces.com" in AI_URL:
                # VolcEngine response format
                if "output" in result and "content" in result["output"]:
                    return {
                        "status": 200,
                        "result": result["output"]["content"]
                    }
                elif result.get("code") == 0:
                    return {
                        "status": 200,
                        "result": result.get("output", {}).get("content", "No response content received")
                    }
            else:
                # OpenAI/DeepSeek response format
                if "choices" in result and len(result["choices"]) > 0:
                    return {
                        "status": 200,
                        "result": result["choices"][0]["message"]["content"]
                    }

            # Error response - try using local AI engine as fallback
            error_msg = result.get("msg", result.get("Message", result.get("error", "AI service temporarily unavailable")))
            local_ai_result = local_ai_engine(prompt)
            if local_ai_result:
                return {"status": 200, "result": local_ai_result}
            return {"status": 500, "error": error_msg}

        except Exception as e:
            # Try local AI engine when network exception occurs
            local_ai_result = local_ai_engine(prompt)
            if local_ai_result:
                return {"status": 200, "result": local_ai_result}
            return {"status": 500, "error": f"Network exception: {str(e)}"}



# ==============================================
# Main Program (completely non-intrusive to native command line)
# ==============================================
def main():
    show_banner()
    if len(sys.argv) < 2:
        print(f"{WAR}Usage:{RES}")
        print(f"  cmdmaster-pro <question>         Generate commands")
        print(f"  cmdmaster-pro --history          View history")
        print(f"  cmdmaster-pro --clear-history    Clear history")
        print(f"  cmdmaster-pro --ai-config        View AI configuration")
        print(f"  cmdmaster-pro --set-ai-url URL   Set AI URL")
        print(f"  cmdmaster-pro --set-ai-token TOKEN Set AI Token")
        print(f"  cmdmaster-pro --set-ai-model MODEL Set AI model\n")
        return

    # View history
    if sys.argv[1] == "--history":
        show_history()
        return

    # Clear history
    if sys.argv[1] == "--clear-history":
        clear_history()
        return

    # View AI configuration
    if sys.argv[1] == "--ai-config":
        show_ai_config()
        return

    # Set AI URL
    if sys.argv[1] == "--set-ai-url" and len(sys.argv) == 3:
        set_ai_config("url", sys.argv[2])
        return

    # Set AI Token
    if sys.argv[1] == "--set-ai-token" and len(sys.argv) == 3:
        set_ai_config("token", sys.argv[2])
        return

    # Set AI Model
    if sys.argv[1] == "--set-ai-model" and len(sys.argv) == 3:
        set_ai_config("model", sys.argv[2])
        return

    # User input
    user_input = " ".join(sys.argv[1:])

    # Determine if it's a direct command (contains common commands or parameters)
    if is_direct_command(user_input):
        # Execute command directly
        print(f"{CMD}⚡ Executing command: {user_input}{RES}")
        try:
            import subprocess
            result = subprocess.run(user_input, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                if result.stdout:
                    print(f"{ACC}{result.stdout}{RES}")
                else:
                    print(f"{ACC}✅ Command executed successfully{RES}")
            else:
                print(f"{ERR}❌ Command execution failed: {result.stderr}{RES}")
        except Exception as e:
            print(f"{ERR}❌ Execution exception: {str(e)}{RES}")
        print()
        return

    # Save to history
    show_suggestions(user_input)
    save_history(user_input)

    # Local priority
    local_cmd = local_engine(user_input)
    if local_cmd:
        print(f"{ACC}✅ Local expert engine{RES}")
        print(f"{CMD}{local_cmd}{RES}\n")
        return

    # Cloud AI (only call when it's a real question)
    print(f"{PRI}🤖 Cloud AI generating...{RES}")
    try:
        res = api("ai", prompt=user_input)
        if res and res.get("status") == 200:
            print(f"{ACC}✅ {res['result']}{RES}\n")
        else:
            error_msg = res.get('error', 'Generation failed') if res else 'Network connection failed'
            print(f"{ERR}❌ {error_msg}{RES}\n")
    except Exception as e:
        print(f"{ERR}❌ API call exception: {str(e)}{RES}\n")

def show_banner():
    print(f"""
{PRI}╔══════════════════════════════════════╗{RES}
{PRI}║   cmdmaster-pro Pro • Intelligent Operations Toolkit    ║{RES}
{PRI}║   History Memory • Smart Completion • Dual Engine      ║{RES}
{PRI}╚══════════════════════════════════════╝{RES}
""")

def show_ai_config():
    """Display current AI configuration"""
    print(f"\n{WAR}📋 Current AI Configuration{RES}")
    print(f"  URL:   {ACC}{AI_URL}{RES}")
    print(f"  Token: {ACC}{AI_TOKEN[:8]}...{RES}" if len(AI_TOKEN) > 8 else f"  Token: {ACC}{AI_TOKEN}{RES}")
    print(f"  Model: {ACC}{AI_MODEL}{RES}\n")

def set_ai_config(config_type, value):
    """Set AI configuration and save to file"""
    config_file = "ai_config.py"

    # Read existing configuration or create new file
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = [
            '# AI Configuration\n',
            '# Modify this file to configure your large model settings\n\n',
            '# VolcEngine configuration (default)\n',
            'AI_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"\n',
            'AI_TOKEN = "71a7a0b1-7c92-4bb5-bfea-577ff9d2d74b"\n',
            'AI_MODEL = "doubao-seed-2-0-pro-260215"\n'
        ]

    # Update corresponding line based on configuration type
    updated = False

    if config_type == "url":
        for i, line in enumerate(lines):
            if line.strip().startswith('AI_URL = '):
                lines[i] = f'AI_URL = "{value}"\n'
                updated = True
                break
        if not updated:
            lines.append(f'AI_URL = "{value}"\n')
        print(f"{ACC}✅ AI URL set to: {value}{RES}")

    elif config_type == "token":
        for i, line in enumerate(lines):
            if line.strip().startswith('AI_TOKEN = '):
                lines[i] = f'AI_TOKEN = "{value}"\n'
                updated = True
                break
        if not updated:
            lines.append(f'AI_TOKEN = "{value}"\n')
        print(f"{ACC}✅ AI Token set{RES}")

    elif config_type == "model":
        for i, line in enumerate(lines):
            if line.strip().startswith('AI_MODEL = '):
                lines[i] = f'AI_MODEL = "{value}"\n'
                updated = True
                break
        if not updated:
            lines.append(f'AI_MODEL = "{value}"\n')
        print(f"{ACC}✅ AI Model set to: {value}{RES}")

    # Save configuration file
    with open(config_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"{WAR}⚠️  Please restart the program for the configuration to take effect{RES}\n")

def is_direct_command(input_text):
    """Determine if user input is a direct command"""
    if not input_text.strip():
        return False

    # Common command list (English commands only)
    common_commands = {
        'ls', 'cd', 'pwd', 'cat', 'less', 'more', 'head', 'tail',
        'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'touch', 'ln',
        'chmod', 'chown', 'chgrp',
        'find', 'grep', 'awk', 'sed', 'cut', 'sort', 'uniq',
        'ps', 'top', 'htop', 'kill', 'pkill', 'killall',
        'df', 'du', 'free', 'vmstat', 'iostat',
        'netstat', 'ss', 'ping', 'traceroute', 'nslookup', 'dig',
        'ssh', 'scp', 'rsync', 'ftp', 'wget', 'curl',
        'tar', 'gzip', 'gunzip', 'zip', 'unzip',
        'git', 'svn', 'hg',
        'docker', 'podman', 'kubectl',
        'systemctl', 'service', 'journalctl',
        'apt', 'yum', 'dnf', 'pacman', 'brew',
        'python', 'python3', 'pip', 'pip3',
        'node', 'npm', 'yarn',
        'mysql', 'psql', 'sqlite3',
        'vim', 'nano', 'emacs',
        'echo', 'printf', 'export', 'source', 'alias',
        'which', 'whereis', 'type', 'man', 'info'
    }

    # Common parameter patterns
    arg_patterns = {
        '-l', '-la', '-lt', '-ltr', '-h', '--help',
        '-v', '--version', '-f', '-r', '-rf', '-R',
        '--all', '--force', '--recursive', '--verbose',
        '-a', '-A', '-i', '-I', '-n', '-N', '-q', '-Q'
    }

    # Split input
    parts = input_text.strip().split()
    if not parts:
        return False

    # Get first word
    first_word = parts[0].lower()

    # If contains Chinese characters, treat as question description, not direct command
    if any('\u4e00' <= char <= '\u9fff' for char in input_text):
        return False

    # Check if first word is a common command
    if first_word in common_commands:
        return True

    # Check if contains pipe or redirection symbols
    if any(char in input_text for char in ['|', '>', '<', '>>', '&&', '||', ';']):
        return True

    # Check if contains common parameters (and first word looks like a command)
    if any(arg in input_text for arg in arg_patterns) and len(first_word) > 1:
        # Ensure first word is mainly alphanumeric
        if first_word.replace('-', '').replace('_', '').isalnum():
            return True

    # Check if contains path operators (and not URL)
    if ('/' in input_text or '~' in input_text) and not input_text.startswith('http'):
        return True

    # If input is short and all English, might be a simple command
    if len(input_text) < 20 and input_text.replace(' ', '').replace('-', '').replace('_', '').isalpha():
        return True

    return False

if __name__ == "__main__":
    main()