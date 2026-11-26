from __future__ import annotations

import json
from typing import Any

from .store import Mailbox
from .tools import TOOL_SCHEMAS, call_tool


def run_agent(
    mailbox: Mailbox,
    client: Any,
    goal: str,
    max_steps: int = 10,
    defense: Any = None,
    tools: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """最简单的 agent loop：模型决策 -> 防御检查 -> 执行工具 -> 结果回填。"""
    active_tools = tools or TOOL_SCHEMAS
    if defense is not None:
        client.system_suffix = defense.system_suffix()

    messages: list[dict[str, Any]] = [{"role": "user", "content": goal}]
    trajectory: list[dict[str, Any]] = []
    repeats: dict[tuple[str, str], int] = {}

    for step in range(1, max_steps + 1):
        action = client.chat(messages, active_tools)
        name = action.get("action")

        if name == "final":
            trajectory.append(
                {"step": step, "type": "final", "text": action.get("text", "")}
            )
            break

        args = action.get("args", {})
        key = (name, json.dumps(args, ensure_ascii=False, sort_keys=True))
        repeats[key] = repeats.get(key, 0) + 1

        allowed, reason = (True, "")
        if repeats[key] > 2:
            allowed, reason = False, "重复调用同一工具超过 2 次，请换一种做法或直接 final"
        elif defense is not None:
            allowed, reason = defense.check_tool_call(name, args, mailbox)

        if allowed:
            try:
                result = call_tool(mailbox, name, args)
            except Exception as exc:  # noqa: BLE001 - 工具错误回传给模型
                result = {"error": f"{type(exc).__name__}: {exc}"}
        else:
            result = {"blocked": True, "reason": reason}

        trajectory.append(
            {
                "step": step,
                "type": "tool_call",
                "name": name,
                "args": args,
                "blocked": not allowed,
            }
        )
        trajectory.append(
            {"step": step, "type": "tool_result", "name": name, "result": result}
        )
        messages.append({"role": "tool", "name": name, "content": result})
    else:
        trajectory.append(
            {"step": max_steps, "type": "error", "text": "达到最大步数，任务未结束"}
        )

    return trajectory
