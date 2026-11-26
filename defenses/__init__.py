from __future__ import annotations

from .base import Defense
from .content_guard import ContentGuard
from .none import NoDefense
from .prompt_hardening import PromptHardening
from .recipient_allowlist import RecipientAllowlist

DEFENSES: dict[str, type[Defense]] = {
    "none": NoDefense,
    "prompt_hardening": PromptHardening,
    "recipient_allowlist": RecipientAllowlist,
    "content_guard": ContentGuard,
}


def build_defense(name: str) -> Defense:
    if name not in DEFENSES:
        raise SystemExit(
            f"unknown defense: {name}; choose from {sorted(DEFENSES)}"
        )
    return DEFENSES[name]()


__all__ = ["Defense", "build_defense", "DEFENSES"]
