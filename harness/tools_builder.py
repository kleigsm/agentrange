from __future__ import annotations

import copy
from typing import Any

from envs.email_assistant.tools import TOOL_SCHEMAS


def build_tools(task: dict[str, Any]) -> list[dict[str, Any]]:
    """按任务覆盖工具描述（用于工具描述投毒实验）。"""
    tools = copy.deepcopy(TOOL_SCHEMAS)
    overrides = task.get("tool_overrides", {})
    for tool in tools:
        override = overrides.get(tool["name"])
        if override:
            tool.update(override)
    return tools
