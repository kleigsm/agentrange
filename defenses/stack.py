from __future__ import annotations

from typing import Any

from .base import Defense


class StackDefense(Defense):
    """把多个防御按顺序叠加。任何一个拦截，整体就拦截。"""

    def __init__(self, defenses: list[Defense]) -> None:
        self.defenses = defenses
        self.name = "+".join(d.name for d in defenses)
        self.description = " + ".join(d.description for d in defenses)

    def system_suffix(self) -> str:
        return "".join(d.system_suffix() for d in self.defenses)

    def check_tool_call(
        self, name: str, args: dict[str, Any], mailbox: Any
    ) -> tuple[bool, str]:
        for defense in self.defenses:
            ok, reason = defense.check_tool_call(name, args, mailbox)
            if not ok:
                return False, f"{defense.name}: {reason}"
        return True, ""
