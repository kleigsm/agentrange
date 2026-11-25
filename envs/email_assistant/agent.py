from __future__ import annotations

from typing import Any

from .store import Mailbox
from .tools import TOOL_SCHEMAS, call_tool


def run_agent(
    mailbox: Mailbox,
    client: Any,
    goal: str,
    max_steps: int = 10,
) -> list[dict[str, Any]]:
    """最简单的 agent loop：模型决策 -> 执行工具 -> 把结果塞回上下文。"""
    messages: list[dict[str, Any]] = [{"role": "user", "content": goal}]
    trajectory: list[dict[str, Any]] = []

    for step in range(1, max_steps + 1):
        action = client.chat(messages, TOOL_SCHEMAS)
        name = action.get("action")

        if name == "final":
            trajectory.append(
                {"step": step, "type": "final", "text": action.get("text", "")}
            )
            break

        args = action.get("args", {})
        try:
            result = call_tool(mailbox, name, args)
        except Exception as exc:  # noqa: BLE001 - 工具错误要回传给模型，而不是崩掉
            result = {"error": f"{type(exc).__name__}: {exc}"}
        trajectory.append(
            {"step": step, "type": "tool_call", "name": name, "args": args}
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
