from __future__ import annotations

from .base import Defense
from .content_guard import ContentGuard
from .content_redaction import ContentRedaction
from .none import NoDefense
from .prompt_hardening import PromptHardening
from .prompt_hardening_neutral import PromptHardeningNeutral
from .recipient_allowlist import RecipientAllowlist
from .stack import StackDefense
from .tool_output_sanitizer import ToolOutputSanitizer

DEFENSES: dict[str, type[Defense]] = {
    "none": NoDefense,
    "prompt_hardening": PromptHardening,
    "prompt_hardening_neutral": PromptHardeningNeutral,
    "recipient_allowlist": RecipientAllowlist,
    "content_guard": ContentGuard,
    "content_redaction": ContentRedaction,
    "tool_output_sanitizer": ToolOutputSanitizer,
}


def build_defense(name: str) -> Defense:
    parts = [part for part in name.split(",") if part]
    if not parts:
        raise SystemExit("empty defense name")
    for part in parts:
        if part not in DEFENSES:
            raise SystemExit(
                f"unknown defense: {part}; choose from {sorted(DEFENSES)}"
            )
    if len(parts) == 1:
        return DEFENSES[parts[0]]()
    return StackDefense([DEFENSES[part]() for part in parts])


__all__ = ["Defense", "build_defense", "DEFENSES"]
