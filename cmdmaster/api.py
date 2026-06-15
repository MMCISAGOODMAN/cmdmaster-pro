import os

import requests

from cmdmaster.config import load_ai_config
from cmdmaster.engines import local_ai_engine
from cmdmaster.utils import get_platform

AI_URL, AI_TOKEN, AI_MODEL = load_ai_config()


def _build_system_prompt():
    platform = get_platform()
    cwd = os.getcwd()
    shell = os.environ.get("SHELL", "bash")
    return (
        f"You are a shell command assistant for {platform}. "
        f"User shell: {shell}. Current directory: {cwd}. "
        "Only return commands and brief explanations, don't use markdown, "
        "maximum 2 commands. Mark the last line as safe / cautious / dangerous"
    )


def call_ai(prompt):
    """Call cloud AI API with automatic fallback to local engine."""
    if not AI_URL or not AI_TOKEN:
        result = local_ai_engine(prompt)
        return {"status": 200, "result": result, "source": "local"}

    try:
        headers = {
            "Authorization": f"Bearer {AI_TOKEN}",
            "Content-Type": "application/json",
        }

        if "ark.cn-beijing.volces.com" in AI_URL:
            data = {
                "model": AI_MODEL,
                "input": [{"role": "user", "content": prompt}],
            }
        else:
            data = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": _build_system_prompt(),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 300,
            }

        response = requests.post(AI_URL, json=data, headers=headers, timeout=15)
        result = response.json()

        if "ark.cn-beijing.volces.com" in AI_URL:
            if "output" in result and "content" in result["output"]:
                return {"status": 200, "result": result["output"]["content"], "source": "cloud"}
            if result.get("code") == 0:
                content = result.get("output", {}).get("content", "")
                if content:
                    return {"status": 200, "result": content, "source": "cloud"}
        elif "choices" in result and result["choices"]:
            return {
                "status": 200,
                "result": result["choices"][0]["message"]["content"],
                "source": "cloud",
            }

        error_msg = result.get(
            "msg", result.get("Message", result.get("error", "AI service temporarily unavailable"))
        )
        local_result = local_ai_engine(prompt)
        return {"status": 200, "result": local_result, "source": "local", "fallback_error": error_msg}

    except Exception as e:
        local_result = local_ai_engine(prompt)
        return {
            "status": 200,
            "result": local_result,
            "source": "local",
            "fallback_error": str(e),
        }
