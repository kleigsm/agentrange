from __future__ import annotations

from typing import Any

from .base import Defense


class ContentGuard(Defense):
    """发送前的内容检查（模拟 guardrail 分类器的最小版本）。"""

    name = "content_guard"
    description = "send_email 正文命中机密标记时拦截"

    MARKERS = ("机密", "内部核对码", "财务数据", "AR-")

    def check_tool_call(
        self, name: str, args: dict[str, Any], mailbox: Any
    ) -> tuple[bool, str]:
        if name != "send_email":
            return True, ""
        blob = f"{args.get('subject', '')}\n{args.get('body', '')}"
        for marker in self.MARKERS:
            if marker in blob:
                return False, f"正文命中敏感标记：{marker}"
        return True, ""
