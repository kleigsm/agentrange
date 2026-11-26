from __future__ import annotations

from typing import Any


class Defense:
    """防御基类。

    两个挂载点：
    - system_suffix(): 加到系统提示末尾（提示词加固）
    - check_tool_call(): 工具执行前拦截（能力沙箱 / 内容过滤）
    """

    name = "base"
    description = ""

    def system_suffix(self) -> str:
        return ""

    def check_tool_call(
        self, name: str, args: dict[str, Any], mailbox: Any
    ) -> tuple[bool, str]:
        return True, ""
