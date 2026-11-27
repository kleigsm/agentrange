"""复制一个 Llama 3.1，只改一处：工具结果的角色从 ipython 改成 user。

目的：验证“工具结果被当成 user 轮”是不是注入成功的关键。
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

OLLAMA = Path.home() / "AppData/Local/Programs/Ollama/ollama.exe"
BASE = "llama3.1:8b"
NEW = "llama3.1-user-tools"
OUT = Path("D:/ollama/Modelfile.llama-user-tools")


def main() -> None:
    out = subprocess.run(
        [str(OLLAMA), "show", BASE, "--modelfile"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout

    match = re.search(r'TEMPLATE """(.*?)"""', out, re.S)
    if not match:
        raise SystemExit("TEMPLATE not found")
    template = match.group(1)

    old = (
        '{{- else if eq .Role "tool" }}'
        "<|start_header_id|>ipython<|end_header_id|>"
    )
    new = (
        '{{- else if eq .Role "tool" }}'
        "<|start_header_id|>user<|end_header_id|>"
    )
    if old not in template:
        raise SystemExit("tool branch not found")
    modified = template.replace(old, new, 1)

    OUT.write_text(
        f'FROM {BASE}\nTEMPLATE """{modified}"""\n',
        encoding="utf-8",
    )
    print(f"wrote {OUT}")
    print("changed tool role: ipython -> user")
    print("create with:")
    print(f'  ollama create {NEW} -f "{OUT}"')


if __name__ == "__main__":
    main()
