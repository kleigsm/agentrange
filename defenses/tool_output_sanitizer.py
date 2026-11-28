from __future__ import annotations

import re
from typing import Any

from .base import Defense

TOKEN_RE = re.compile(r"<\|[^|>]*\|>")
INST_RE = re.compile(r"\[/?INST\]")


class ToolOutputSanitizer(Defense):
    """在工具结果进入模型之前，中和特殊 token。

    不判断内容是否恶意，只保证“数据里不会出现可被当成结构 token 的字符串”。
    """

    name = "tool_output_sanitizer"
    description = "把工具结果里的 <|...|> 和 [INST] 中和为非 token 的 [TOKEN] / 【INST】"

    def check_tool_call(
        self, name: str, args: dict[str, Any], mailbox: Any
    ) -> tuple[bool, str]:
        return True, ""

    def sanitize(self, value: Any) -> Any:
        if isinstance(value, str):
            value = TOKEN_RE.sub("[TOKEN]", value)
            # 必须换成非 token：换成 [INST] 仍会被 Mistral 当成结构 token
            value = INST_RE.sub("【INST】", value)
            return value
        if isinstance(value, dict):
            return {key: self.sanitize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.sanitize(item) for item in value]
        return value
