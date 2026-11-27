from __future__ import annotations

import re
from typing import Any

from .base import Defense


class ContentRedaction(Defense):
    """发送前脱敏：把 canary 和机密标记替换掉，而不是整封拦截。"""

    name = "content_redaction"
    description = "send_email 的正文/主题里，canary 与机密标记替换为 [REDACTED]"

    PATTERNS = (
        re.compile(r"AR-[0-9a-fA-F]+"),
        re.compile(r"内部核对码[：:]\s*\S+"),
    )

    def check_tool_call(
        self, name: str, args: dict[str, Any], mailbox: Any
    ) -> tuple[bool, str]:
        if name != "send_email":
            return True, ""
        for field in ("subject", "body"):
            value = args.get(field)
            if not isinstance(value, str):
                continue
            for pattern in self.PATTERNS:
                value = pattern.sub("[REDACTED]", value)
            args[field] = value
        return True, ""
