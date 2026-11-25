from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from envs.email_assistant.llm import OllamaClient, OpenAICompatClient, ScriptedClient


def load_env(path: str = ".env") -> None:
    """极简 .env 读取：KEY=VALUE，忽略注释和空行。"""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def make_client_factory(model_arg: str, canary: str) -> Callable[[], object]:
    """返回一个工厂：每次调用创建一个新的 LLM client（便于批量实验互不污染）。"""
    if model_arg == "scripted":
        return lambda: ScriptedClient(canary=canary)

    if model_arg == "api":
        base = os.environ.get("AR_API_BASE", "https://api.deepseek.com/v1")
        key = os.environ.get("AR_API_KEY", "")
        model = os.environ.get("AR_API_MODEL", "deepseek-chat")
        if not key or key == "sk-replace-me":
            raise SystemExit(
                "缺少 AR_API_KEY。复制 .env.example 为 .env，填入你的 key，再运行。"
            )
        return lambda: OpenAICompatClient(model=model, base_url=base, api_key=key)

    if model_arg.startswith("ollama:"):
        model = model_arg.split(":", 1)[1]
        return lambda: OllamaClient(model=model)

    raise SystemExit("未知的 --model。可用：scripted | api | ollama:<模型名>")
