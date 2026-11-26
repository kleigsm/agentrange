from __future__ import annotations

from .base import Defense


class NoDefense(Defense):
    name = "none"
    description = "无防御基线"
