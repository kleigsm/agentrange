"""生成小红书 3:4 封面（1080x1440）。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1440
BG = "#0B1220"
PANEL = "#111C33"
WHITE = "#F8FAFC"
GRAY = "#94A3B8"
SOFT = "#CBD5E1"
AMBER = "#F59E0B"
RED = "#F87171"

OUT = Path("docs/07-文章/cover-xhs.png")

BOLD = "C:/Windows/Fonts/msyhbd.ttc"
REG = "C:/Windows/Fonts/msyh.ttc"
MONO = "C:/Windows/Fonts/consola.ttf"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rectangle([0, 0, 14, H], fill=AMBER)
d.ellipse([W - 260, -160, W + 160, 260], fill="#101A2E")

label = ImageFont.truetype(REG, 30)
title = ImageFont.truetype(BOLD, 92)
sub = ImageFont.truetype(REG, 38)
mono = ImageFont.truetype(MONO, 64)
small = ImageFont.truetype(REG, 30)

d.text((80, 100), "AGENT SECURITY · 实验", font=label, fill=GRAY)
d.text((80, 230), "提示词加固，", font=title, fill=WHITE)
d.text((80, 350), "反而让攻击", font=title, fill=WHITE)
d.text((80, 470), "翻倍？", font=title, fill=AMBER)
d.text((80, 620), "LLM Agent 注入实验", font=sub, fill=SOFT)

d.rounded_rectangle([80, 760, 1000, 1010], radius=24, fill=PANEL, outline="#1E293B")
d.text((120, 800), "ASR（攻击成功率）", font=small, fill=GRAY)
d.text((120, 860), "0.50 → 1.00", font=mono, fill=AMBER)
d.text((120, 940), "加固后 20/20 全中", font=small, fill=RED)

d.text((80, 1120), "为什么“防御”会变成“助攻”？", font=sub, fill=WHITE)
d.text((80, 1190), "结构 token · 模板相关 · 三层防御", font=small, fill=GRAY)
d.text((80, 1320), "github.com/kleigsm/agentrange", font=small, fill="#64748B")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, quality=95)
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
