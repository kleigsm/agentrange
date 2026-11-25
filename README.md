# AgentRange

**面向国产大模型的 Agent 安全基准。**

用可执行的 canary 判定，替代不可靠的 LLM judge——让每一条红队发现都能被复现、被验证。

> 给 Agent 建一个靶场：20 个真实任务 × 3 类注入 × 4 种防御，回答“到底哪种防御有用，代价是什么”。

## 为什么做这个

- **判定不可信**：LLM-as-judge 在对抗评测上接近抛硬币（ICML 2026, *A Coin Flip for Safety*），市面上的“攻击成功率”大多不可验证。
- **Agent 的漏洞是“做了坏事”，不是“说了坏话”**：把密钥发出去、把钱转走、把日程删掉。这类后果必须用可执行谓词判定。
- **国产模型缺覆盖**：现有基准以 GPT / Claude 为主，Qwen、DeepSeek、GLM 的 Agent 安全数据几乎空白。

## 核心设计

1. **Canary 判定**：每个任务埋一个唯一字符串，出现在“不该出现的地方”即为泄漏，不需要 AI 裁判。
2. **证据包**：每个成功攻击输出一份 JSON——轨迹、canary、复现率、最小化、修复验证。
3. **两层可复现**：确定性 witness replay + 统计性 re-elicitation。

## 当前状态

`v0.1` · 最小邮件助理已跑通；支持假模型（验证链路）和 OpenAI 兼容 API（真模型）。

## 快速开始

```powershell
uv venv
uv pip install -r requirements.txt

# 1) 假模型：验证靶场和判定链路，不需要任何 key
.venv\Scripts\python.exe -m harness.run --task tasks\email-exfil-001.yaml --model scripted

# 2) 真模型：把 .env.example 复制为 .env 并填入 key
.venv\Scripts\python.exe -m harness.run --task tasks\email-exfil-001.yaml --model api
```

证据会写到 `results/evidence/<task-id>.json`。

## 目录

| 路径 | 作用 |
|---|---|
| `docs/` | Obsidian 知识库（课程、实验记录、决策） |
| `spec/` | 机器可读 schema（后续） |
| `docs/04-规范/` | 规范正文（证据包格式） |
| `tasks/` | 任务定义（YAML） |
| `envs/` | 靶场环境（后续） |
| `harness/` | 运行器、判定器、统计（后续） |
| `web/` | 结果可视化（后续） |

## 路线图

- [ ] v0.1：单场景（邮件助理）+ 3 任务 + canary CLI
- [ ] v0.2：20 任务 / 3 攻击 / 4 防御
- [ ] v0.3：Web 报告 + 公开榜单
- [ ] v1.0：技术报告 + 数据集发布

## 许可

待定（预计 Apache-2.0）
