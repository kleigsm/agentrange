from __future__ import annotations

from typing import Any

from .base import Defense


class RecipientAllowlist(Defense):
    """能力沙箱的最简版：只允许发给通讯录里的地址。"""

    name = "recipient_allowlist"
    description = "send_email 的收件人必须在通讯录白名单内"

    def check_tool_call(
        self, name: str, args: dict[str, Any], mailbox: Any
    ) -> tuple[bool, str]:
        if name != "send_email":
            return True, ""
        to = str(args.get("to", ""))
        contacts = mailbox.search_contacts("")
        allowed = {c["email"] for c in contacts}
        if any(email in to for email in allowed):
            return True, ""
        return False, f"收件人 {to!r} 不在通讯录白名单内"
