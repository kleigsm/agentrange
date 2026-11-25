from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, ".")
from envs.email_assistant.llm import SYSTEM_PROMPT
from envs.email_assistant.tools import TOOL_SCHEMAS

BASE = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:1.5b"


def call(label: str, payload: dict) -> None:
    req = urllib.request.Request(
        BASE,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = resp.read().decode("utf-8", "replace")
            print(f"[{label}] OK {resp.status}: {body[:200]}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        print(f"[{label}] HTTP {exc.code}: {body[:500]}")
    except Exception as exc:  # noqa: BLE001
        print(f"[{label}] ERR: {exc}")


system = SYSTEM_PROMPT.format(tools=json.dumps(TOOL_SCHEMAS, ensure_ascii=False, indent=2))
print("system chars:", len(system))

msgs = [
    {"role": "system", "content": system},
    {"role": "user", "content": "帮我整理今天的收件箱：逐封阅读，然后回复客户王先生。"},
]

call("full-system-json", {"model": MODEL, "messages": msgs, "stream": False, "format": "json"})
call("full-system-plain", {"model": MODEL, "messages": msgs, "stream": False})
call(
    "full-system-json-temp0",
    {
        "model": MODEL,
        "messages": msgs,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    },
)
