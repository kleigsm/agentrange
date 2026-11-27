"""把 Markdown 文章转成知乎友好的纯文本。

知乎编辑器不解析 Markdown，直接粘贴会看到 ** 和 |。
这个脚本：
  - 去掉 frontmatter / H1
  - 标题变成【标题】
  - 表格转成条目列表
  - 代码块缩进
  - 去掉 ** / * / 反引号
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path("docs/07-文章/2026-11-28-提示词加固为什么帮倒忙.md")
OUT = Path("docs/07-文章/2026-11-28-知乎版.txt")


def parse_table(lines: list[str], start: int) -> tuple[list[str], int]:
    block = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        block.append(lines[i].strip())
        i += 1
    rows = []
    for line in block:
        raw = line
        if raw.startswith("|"):
            raw = raw[1:]
        if raw.endswith("|") and not raw.endswith("\\|"):
            raw = raw[:-1]
        cells = [
            c.strip().replace("\\|", "|")
            for c in re.split(r"(?<!\\)\|", raw)
        ]
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        rows.append(cells)
    return rows, i


def table_to_text(rows: list[str]) -> list[str]:
    if not rows:
        return []
    header = rows[0]
    out = []
    for row in rows[1:]:
        parts = []
        for idx, value in enumerate(row):
            key = header[idx] if idx < len(header) else f"列{idx + 1}"
            parts.append(f"{key}：{value}")
        out.append("- " + "；".join(parts))
    return out


def convert(text: str) -> str:
    text = re.sub(r"(?s)^---.*?---\s*", "", text)
    lines = text.splitlines()

    # 去掉第一个 H1
    for idx, line in enumerate(lines):
        if line.startswith("# "):
            lines.pop(idx)
            break

    out: list[str] = []
    i = 0
    in_code = False
    code_buf: list[str] = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                out.extend("    " + c for c in code_buf)
                out.append("")
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if stripped.startswith("|"):
            rows, i = parse_table(lines, i)
            out.extend(table_to_text(rows))
            out.append("")
            continue

        if stripped.startswith("### "):
            out.append(stripped[4:])
            out.append("")
        elif stripped.startswith("## "):
            out.append(f"【{stripped[3:]}】")
            out.append("")
        elif stripped.startswith("> "):
            out.append(stripped[2:])
        elif stripped == ">":
            out.append("")
        elif stripped == "---":
            out.append("")
        else:
            out.append(line)
        i += 1

    result = "\n".join(out)
    result = re.sub(r"\*\*([^*]+)\*\*", r"\1", result)
    result = re.sub(r"\*([^*\n]+)\*", r"\1", result)
    result = re.sub(r"`([^`]+)`", r"\1", result)
    result = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1（\2）", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip() + "\n"


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    result = convert(text)
    OUT.write_text(result, encoding="utf-8")
    print(f"wrote {OUT} ({len(result)} chars)")


if __name__ == "__main__":
    main()
