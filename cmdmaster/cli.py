#!/usr/bin/env python3
import argparse
import subprocess
import sys

from cmdmaster import __version__, api
from cmdmaster.cache import clear_cache, get_cached, set_cached
from cmdmaster.completion import generate_bash_completion, generate_zsh_completion
from cmdmaster.config import (
    get_config_dir,
    get_config_file,
    is_ai_configured,
    load_ai_config,
    reload_module_config,
    set_ai_config,
)
from cmdmaster.engines import local_ai_engine, local_engine
from cmdmaster.explain import explain_command
from cmdmaster.favorites import add_favorite, list_favorites, remove_favorite
from cmdmaster.history import (
    clear_history,
    export_history,
    get_smart_suggestions,
    import_history,
    load_history,
    save_history,
    search_history,
)
from cmdmaster.output import format_json_explain, format_json_result
from cmdmaster.safety import (
    classify_command,
    confirm_execution,
    get_warning_message,
    parse_ai_safety_label,
)
from cmdmaster.templates import (
    list_user_templates,
    match_user_template,
    remove_user_template,
    save_user_template,
)
from cmdmaster import theme
from cmdmaster.utils import copy_to_clipboard, get_platform, primary_command

INTERACTIVE_HELP = """
Interactive commands:
  :help              Show this help
  :history           Show recent queries
  :search <text>     Search history
  :suggest [text]    Show suggestions (!1..!9 to pick)
  :favorite add TEXT Save to favorites
  :favorite list     List favorites
  :favorite rm TEXT  Remove favorite
  :template list     List custom templates
  :local on|off      Toggle local-only mode
  :clear-cache       Clear result cache
  exit / quit / q    Exit interactive mode
"""


def show_banner():
    print(f"""
{theme.PRI("╔══════════════════════════════════════╗")}
{theme.PRI("║   cmdmaster-pro • Intelligent Operations Toolkit       ║")}
{theme.PRI(f"║   History • Smart Completion • Dual Engine • v{__version__}   ║")}
{theme.PRI("╚══════════════════════════════════════╝")}
{theme.DIM(f"Platform: {get_platform()}")}
""")


def show_history():
    history = load_history()
    if not history:
        print(f"\n{theme.DIM('No history records')}\n")
        return
    print(f"\n{theme.WAR('📜 History (last 30 entries)')}")
    for i, line in enumerate(history, 1):
        print(f"{theme.ACC(f'{i:2d}.')} {line}")
    print()


def show_search_results(query):
    results = search_history(query)
    if not results:
        print(f"\n{theme.DIM(f'No matches for {query!r}')}\n")
        return
    print(f"\n{theme.WAR(f'🔍 Search results for {query!r}')}")
    for i, line in enumerate(results, 1):
        print(f"{theme.ACC(f'{i:2d}.')} {line}")
    print()


def show_suggestions(input_text, limit=4, numbered=False):
    suggestions = get_smart_suggestions(input_text, limit=limit)
    if not suggestions:
        return suggestions
    print(theme.WAR("💡 Smart completion (history + recommendations):"))
    for i, s in enumerate(suggestions, 1):
        prefix = f"{theme.ACC(f'!{i}')} " if numbered else f"{theme.ACC('→')} "
        print(f"  {prefix}{s}")
    return suggestions


def show_favorites():
    favorites = list_favorites()
    if not favorites:
        print(f"\n{theme.DIM('No favorites saved')}\n")
        return
    print(f"\n{theme.WAR('⭐ Favorites')}")
    for i, line in enumerate(favorites, 1):
        print(f"{theme.ACC(f'{i:2d}.')} {line}")
    print()


def show_templates():
    templates = list_user_templates()
    if not templates:
        print(f"\n{theme.DIM('No custom templates')}")
        print(theme.DIM(f"  Add via: cmdmaster-pro --template add \"keyword\" \"command\""))
        print(theme.DIM(f"  File: {get_config_dir()}/templates.json\n"))
        return
    print(f"\n{theme.WAR('📋 Custom Templates')}")
    for key, cmd in templates.items():
        print(f"  {theme.ACC(key)} → {theme.CMD(cmd)}")
    print()


def show_ai_config():
    url, token, model = load_ai_config()
    print(f"\n{theme.WAR('📋 Current AI Configuration')}")
    print(f"  Config file: {theme.DIM(get_config_file())}")
    if url:
        print(f"  URL:   {theme.ACC(url)}")
    else:
        print(f"  URL:   {theme.DIM('(not configured)')}")
    if token:
        masked = f"{token[:8]}..." if len(token) > 8 else token
        print(f"  Token: {theme.ACC(masked)}")
    else:
        print(f"  Token: {theme.DIM('(not configured — local engine only)')}")
    print(f"  Model: {theme.ACC(model)}\n")


def print_result(cmd_text, source="local", safety_level="safe"):
    if safety_level == "dangerous":
        print(theme.ERR("⚠️  DANGEROUS — review carefully before running"))
    elif safety_level == "cautious":
        print(theme.WAR("⚠️  CAUTION — verify before executing"))

    warning = get_warning_message(cmd_text)
    if warning and safety_level == "safe":
        safety_level = classify_command(cmd_text)
        if safety_level == "cautious":
            print(theme.WAR(f"⚠️  CAUTION: {warning}"))
        elif safety_level == "dangerous":
            print(theme.ERR(f"⚠️  DANGEROUS: {warning}"))

    source_label = {
        "local": "Local expert engine",
        "cloud": "Cloud AI",
        "local-fallback": "Local fallback engine",
        "template": "User template",
        "cache": "Cached result",
    }.get(source, source)
    print(theme.ACC(f"✅ {source_label}"))
    print(f"{theme.CMD(cmd_text)}\n")


def generate_command(user_input, explain=False, local_only=False, use_cache=True, json_mode=False):
    """Generate a command from natural language input."""
    if not json_mode:
        show_suggestions(user_input, numbered=False)
    save_history(user_input)

    user_tpl = match_user_template(user_input)
    if user_tpl:
        safety = classify_command(user_tpl)
        if not json_mode:
            if explain:
                print(f"{theme.PRI('📖 Explanation:')} Matched user template\n")
            print_result(user_tpl, source="template", safety_level=safety)
        return user_tpl, "template", safety

    local_cmd = local_engine(user_input)
    if local_cmd:
        if not json_mode:
            if explain:
                print(f"{theme.PRI('📖 Explanation:')} Matched local expert rule\n")
            print_result(local_cmd, source="local")
        set_cached(user_input, local_cmd, "local")
        return local_cmd, "local", classify_command(primary_command(local_cmd))

    if use_cache:
        cached = get_cached(user_input)
        if cached:
            result = cached["result"]
            source = cached.get("source", "cache")
            safety = classify_command(primary_command(result))
            if not json_mode:
                print(theme.DIM("(from cache)"))
                print_result(result, source="cache", safety_level=safety)
            return result, "cache", safety

    if local_only:
        result = local_ai_engine(user_input)
        if not json_mode:
            if explain:
                print(f"{theme.PRI('📖 Explanation:')} Engine: local (forced)\n")
            print_result(result, source="local-fallback")
        set_cached(user_input, result, "local-fallback")
        return result, "local-fallback", classify_command(primary_command(result))

    url, token, _ = load_ai_config()
    if not is_ai_configured(url, token):
        if not json_mode:
            print(theme.WAR("ℹ️  AI not configured — using local engine"))
            print(theme.DIM("  Set via: cmdmaster-pro --set-ai-token TOKEN\n"))
        result = local_ai_engine(user_input)
        if not json_mode:
            print_result(result, source="local-fallback")
        set_cached(user_input, result, "local-fallback")
        return result, "local-fallback", classify_command(primary_command(result))

    if not json_mode:
        print(theme.PRI("🤖 Cloud AI generating..."))
    res = api.call_ai(user_input)
    if res and res.get("status") == 200:
        raw = res["result"]
        source = res.get("source", "cloud")
        if source == "local":
            source = "local-fallback"
            if res.get("fallback_error") and not json_mode:
                print(theme.WAR(f"⚠️  Cloud unavailable: {res['fallback_error']}"))

        label, body = parse_ai_safety_label(raw)
        if not json_mode:
            if explain:
                print(f"{theme.PRI('📖 Explanation:')} Safety={label}, Engine={source}\n")
            print_result(body, source=source, safety_level=label)
        set_cached(user_input, body, source)
        return body, source, label

    error_msg = res.get("error", "Generation failed") if res else "Network connection failed"
    if not json_mode:
        print(f"{theme.ERR(f'❌ {error_msg}')}\n")
    return None, None, "safe"


def is_direct_command(input_text):
    if not input_text.strip():
        return False

    common_commands = {
        "ls", "cd", "pwd", "cat", "less", "more", "head", "tail",
        "cp", "mv", "rm", "mkdir", "rmdir", "touch", "ln",
        "chmod", "chown", "chgrp",
        "find", "grep", "awk", "sed", "cut", "sort", "uniq",
        "ps", "top", "htop", "kill", "pkill", "killall",
        "df", "du", "free", "vmstat", "iostat",
        "netstat", "ss", "ping", "traceroute", "nslookup", "dig",
        "ssh", "scp", "rsync", "ftp", "wget", "curl",
        "tar", "gzip", "gunzip", "zip", "unzip",
        "git", "svn", "hg",
        "docker", "podman", "kubectl",
        "systemctl", "service", "journalctl",
        "apt", "yum", "dnf", "pacman", "brew",
        "python", "python3", "pip", "pip3",
        "node", "npm", "yarn",
        "mysql", "psql", "sqlite3",
        "vim", "nano", "emacs",
        "echo", "printf", "export", "source", "alias",
        "which", "whereis", "type", "man", "info",
    }

    arg_patterns = {
        "-l", "-la", "-lt", "-ltr", "-h", "--help",
        "-v", "--version", "-f", "-r", "-rf", "-R",
        "--all", "--force", "--recursive", "--verbose",
    }

    parts = input_text.strip().split()
    if not parts:
        return False

    first_word = parts[0].lower()

    if any("\u4e00" <= char <= "\u9fff" for char in input_text):
        return False

    if first_word in common_commands:
        return True

    if any(char in input_text for char in ["|", ">", "<", ">>", "&&", "||", ";"]):
        return True

    if any(arg in input_text for arg in arg_patterns) and len(first_word) > 1:
        if first_word.replace("-", "").replace("_", "").isalnum():
            return True

    if ("/" in input_text or "~" in input_text) and not input_text.startswith("http"):
        return True

    if len(input_text) < 20 and input_text.replace(" ", "").replace("-", "").replace("_", "").isalpha():
        return True

    return False


def execute_command(user_input, force=False, json_mode=False):
    level = classify_command(user_input)
    if level == "dangerous" and not force:
        if not confirm_execution(user_input, level="dangerous"):
            if not json_mode:
                print(f"{theme.WAR('Cancelled.')}\n")
            return False
    elif level == "cautious" and not force:
        warning = get_warning_message(user_input)
        if warning and not json_mode:
            print(theme.WAR(f"⚠️  CAUTION: {warning}"))

    if not json_mode:
        print(theme.CMD(f"⚡ Executing command: {user_input}"))
    try:
        result = subprocess.run(user_input, shell=True, capture_output=True, text=True)
        if json_mode:
            print(json.dumps({
                "command": user_input,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }, ensure_ascii=False, indent=2))
        elif result.returncode == 0:
            if result.stdout:
                print(theme.ACC(result.stdout))
            else:
                print(theme.ACC("✅ Command executed successfully"))
        else:
            print(theme.ERR(f"❌ Command execution failed: {result.stderr}"))
    except Exception as e:
        if json_mode:
            print(json.dumps({"command": user_input, "error": str(e)}))
        else:
            print(theme.ERR(f"❌ Execution exception: {str(e)}"))
    if not json_mode:
        print()
    return True


def handle_decode(command, json_mode=False):
    explanation = explain_command(command)
    safety = classify_command(command)
    if json_mode:
        print(format_json_explain(command, explanation, safety))
    else:
        print(f"\n{theme.WAR('🔍 Command decode')}")
        print(f"  {theme.CMD(command)}")
        print(f"  {theme.PRI('→')} {explanation}")
        print(f"  {theme.DIM(f'Safety: {safety}')}\n")


def handle_interactive_builtin(user_input, session):
    text = user_input.strip()
    lower = text.lower()

    if lower in (":help", "help", "?"):
        print(theme.DIM(INTERACTIVE_HELP))
        return True

    if lower in (":history", "history"):
        show_history()
        return True

    if lower.startswith(":search ") or lower.startswith("search "):
        query = text.split(maxsplit=1)[1] if " " in text else ""
        show_search_results(query)
        return True

    if lower.startswith(":suggest"):
        prefix = text.split(maxsplit=1)[1] if " " in text else ""
        session["last_suggestions"] = show_suggestions(prefix, limit=9, numbered=True) or []
        print()
        return True

    if lower.startswith(":favorite"):
        parts = text.split(maxsplit=2)
        action = parts[1].lower() if len(parts) > 1 else "list"
        if action in ("list", "ls"):
            show_favorites()
        elif action == "add" and len(parts) > 2:
            msg = theme.ACC("⭐ Added to favorites") if add_favorite(parts[2]) else theme.ERR("❌ Failed")
            print(f"{msg}\n")
        elif action in ("rm", "remove") and len(parts) > 2:
            msg = theme.ACC("✅ Removed") if remove_favorite(parts[2]) else theme.WAR("Not found")
            print(f"{msg}\n")
        else:
            print(f"{theme.WAR('Usage: :favorite add|list|rm <text>')}\n")
        return True

    if lower in (":template list", ":templates"):
        show_templates()
        return True

    if lower == ":clear-cache":
        msg = theme.ACC("✅ Cache cleared") if clear_cache() else theme.WAR("Cache already empty")
        print(f"{msg}\n")
        return True

    if lower.startswith(":local"):
        parts = lower.split()
        if len(parts) == 2 and parts[1] in ("on", "off"):
            session["local_only"] = parts[1] == "on"
            state = "ON" if session["local_only"] else "OFF"
            print(f"{theme.ACC(f'Local-only mode: {state}')}\n")
        else:
            state = "ON" if session.get("local_only") else "OFF"
            print(f"{theme.WAR(f'Local-only mode is {state}. Use :local on|off')}\n")
        return True

    return False


def resolve_interactive_pick(user_input, session):
    if user_input.startswith("!") and user_input[1:].isdigit():
        idx = int(user_input[1:]) - 1
        picks = session.get("last_suggestions", [])
        if 0 <= idx < len(picks):
            return picks[idx]
    return user_input


def interactive_loop(args):
    session = {"local_only": args.local_only, "last_suggestions": []}
    print(f"{theme.DIM('Interactive mode — type :help for commands, exit to quit')}\n")
    while True:
        try:
            raw = input(f"{theme.PRI('cmdmaster-pro>')} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in ("exit", "quit", "q"):
            break
        if handle_interactive_builtin(raw, session):
            continue

        user_input = resolve_interactive_pick(raw, session)
        session["last_suggestions"] = get_smart_suggestions(user_input, limit=9)

        merged = argparse.Namespace(**vars(args))
        merged.local_only = session.get("local_only", args.local_only)
        process_input(user_input, merged)


def process_input(user_input, args):
    if args.decode:
        handle_decode(user_input, json_mode=args.json)
        return

    if is_direct_command(user_input) and not args.dry_run:
        execute_command(user_input, force=args.yes, json_mode=args.json)
        return

    cmd_text, source, safety = generate_command(
        user_input,
        explain=args.explain,
        local_only=args.local_only,
        use_cache=not args.no_cache,
        json_mode=args.json,
    )

    if args.json:
        print(format_json_result(user_input, cmd_text, source, safety))
        return

    if not cmd_text:
        return

    runnable = primary_command(cmd_text)

    if args.copy:
        if copy_to_clipboard(runnable):
            print(theme.ACC(f"📋 Copied to clipboard: {runnable}\n"))
        else:
            print(f"{theme.WAR('⚠️  Could not copy to clipboard')}\n")

    if args.run and runnable:
        level = safety if safety != "safe" else classify_command(runnable)
        if level in ("dangerous", "cautious") and not args.yes:
            if not confirm_execution(runnable, level=level):
                print(f"{theme.WAR('Execution cancelled.')}\n")
                return
        execute_command(runnable, force=args.yes)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cmdmaster-pro",
        description="Intelligent Operations Toolkit — generate shell commands from natural language",
    )
    parser.add_argument("query", nargs="*", help="Natural language query or command")
    parser.add_argument("--history", action="store_true", help="View command history")
    parser.add_argument("--clear-history", action="store_true", help="Clear command history")
    parser.add_argument("--export-history", metavar="FILE", help="Export history to JSON file")
    parser.add_argument("--import-history", metavar="FILE", help="Import history from JSON file")
    parser.add_argument("--ai-config", action="store_true", help="View AI configuration")
    parser.add_argument("--set-ai-url", metavar="URL", help="Set AI API URL")
    parser.add_argument("--set-ai-token", metavar="TOKEN", help="Set AI API token")
    parser.add_argument("--set-ai-model", metavar="MODEL", help="Set AI model name")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("-e", "--explain", action="store_true", help="Show explanation for generated command")
    parser.add_argument("-d", "--decode", action="store_true", help="Explain what a shell command does")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy generated command to clipboard")
    parser.add_argument("-x", "--run", action="store_true", help="Execute generated command after confirmation")
    parser.add_argument("-L", "--local-only", action="store_true", help="Use local engine only, skip cloud AI")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Generate only, never execute directly")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation for risky commands")
    parser.add_argument("--json", action="store_true", help="Output results as JSON (for scripting)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--no-cache", action="store_true", help="Skip result cache")
    parser.add_argument("--clear-cache", action="store_true", help="Clear result cache")
    parser.add_argument("--search", metavar="QUERY", help="Search command history")
    parser.add_argument("--suggest", nargs="?", const="", metavar="PREFIX", help="Show smart suggestions")
    parser.add_argument("--favorite", nargs="+", metavar="ARGS", help="Manage favorites: list | add TEXT | remove TEXT")
    parser.add_argument("--template", nargs="+", metavar="ARGS", help="Manage templates: list | add KEY CMD | remove KEY")
    parser.add_argument("--completion", choices=["bash", "zsh"], help="Print shell completion script")
    parser.add_argument("--stdin", action="store_true", help="Read query from stdin")
    parser.add_argument("-V", "--version", action="version", version=f"cmdmaster-pro {__version__}")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.no_color:
        theme.set_colors(False)

    if args.completion:
        print(generate_bash_completion() if args.completion == "bash" else generate_zsh_completion())
        return

    if args.clear_cache:
        show_banner()
        print(theme.ACC("✅ Cache cleared\n") if clear_cache() else theme.WAR("Cache already empty\n"))
        return

    if args.history:
        show_banner()
        show_history()
        return

    if args.clear_history:
        show_banner()
        print(theme.ACC("✅ History cleared\n") if clear_history() else theme.ERR("❌ Clear failed\n"))
        return

    if args.export_history:
        show_banner()
        ok = export_history(args.export_history)
        print(theme.ACC(f"✅ Exported to {args.export_history}\n") if ok else theme.ERR("❌ Export failed\n"))
        return

    if args.import_history:
        show_banner()
        ok = import_history(args.import_history)
        print(theme.ACC(f"✅ Imported from {args.import_history}\n") if ok else theme.ERR("❌ Import failed\n"))
        return

    if args.search is not None:
        show_banner()
        show_search_results(args.search)
        return

    if args.suggest is not None:
        show_banner()
        show_suggestions(args.suggest, limit=10)
        print()
        return

    if args.favorite is not None:
        show_banner()
        action = args.favorite[0].lower() if args.favorite else "list"
        if action == "list":
            show_favorites()
        elif action == "add" and len(args.favorite) > 1:
            text = " ".join(args.favorite[1:])
            print(theme.ACC("⭐ Added\n") if add_favorite(text) else theme.ERR("❌ Failed\n"))
        elif action in ("remove", "rm") and len(args.favorite) > 1:
            text = " ".join(args.favorite[1:])
            print(theme.ACC("✅ Removed\n") if remove_favorite(text) else theme.WAR("Not found\n"))
        else:
            print(f"{theme.WAR('Usage: --favorite list|add TEXT|remove TEXT')}\n")
        return

    if args.template is not None:
        show_banner()
        action = args.template[0].lower() if args.template else "list"
        if action == "list":
            show_templates()
        elif action == "add" and len(args.template) >= 3:
            key, cmd = args.template[1], " ".join(args.template[2:])
            print(theme.ACC("✅ Template saved\n") if save_user_template(key, cmd) else theme.ERR("❌ Failed\n"))
        elif action in ("remove", "rm") and len(args.template) > 1:
            key = " ".join(args.template[1:])
            print(theme.ACC("✅ Removed\n") if remove_user_template(key) else theme.WAR("Not found\n"))
        else:
            print(f"{theme.WAR('Usage: --template list|add KEY CMD|remove KEY')}\n")
        return

    if args.ai_config:
        show_banner()
        show_ai_config()
        return

    if args.set_ai_url:
        show_banner()
        set_ai_config("url", args.set_ai_url)
        reload_module_config()
        print(f"{theme.ACC(f'✅ AI URL set to: {args.set_ai_url}')}")
        print(f"{theme.ACC(f'✅ Saved to: {get_config_file()}')}\n")
        return

    if args.set_ai_token:
        show_banner()
        set_ai_config("token", args.set_ai_token)
        reload_module_config()
        print(f"{theme.ACC('✅ AI Token set')}")
        print(f"{theme.ACC(f'✅ Saved to: {get_config_file()}')}\n")
        return

    if args.set_ai_model:
        show_banner()
        set_ai_config("model", args.set_ai_model)
        reload_module_config()
        print(f"{theme.ACC(f'✅ AI Model set to: {args.set_ai_model}')}")
        print(f"{theme.ACC(f'✅ Saved to: {get_config_file()}')}\n")
        return

    if args.stdin:
        query = sys.stdin.read().strip()
        if not query:
            return
        if not args.json:
            show_banner()
        process_input(query, args)
        return

    if args.json and args.query:
        process_input(" ".join(args.query), args)
        return

    show_banner()

    if args.interactive or not args.query:
        interactive_loop(args)
        return

    user_input = " ".join(args.query)
    process_input(user_input, args)


if __name__ == "__main__":
    main()
