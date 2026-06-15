import json

from cmdmaster.utils import extract_shell_commands, get_platform, primary_command


def format_json_result(query, cmd_text, source, safety, cached=False, extra=None):
    commands = extract_shell_commands(cmd_text) if cmd_text else []
    payload = {
        "query": query,
        "command": primary_command(cmd_text) if cmd_text else "",
        "commands": commands,
        "output": cmd_text or "",
        "source": source,
        "safety": safety,
        "platform": get_platform(),
        "cached": cached,
    }
    if extra:
        payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def format_json_explain(command, explanation, safety):
    return json.dumps(
        {
            "command": command,
            "explanation": explanation,
            "safety": safety,
            "platform": get_platform(),
        },
        ensure_ascii=False,
        indent=2,
    )
