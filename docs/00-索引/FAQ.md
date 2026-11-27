---
tags: [索引, FAQ]
---

# FAQ

## 这是不是一个漏洞扫描器？

不是。AgentRange 不攻击真实系统，只在**本地模拟邮箱**里测 Agent 的行为。它的价值是“可复现地测量”，不是“批量扫目标”。

## 为什么不用 LLM-as-judge？

LLM judge 在对抗场景下不稳定：同一份轨迹跑两次可能给出不同结论，而且容易把“模型尝试了”当成“模型成功了”。

AgentRange 用**可执行 canary oracle**：canary 有没有出现在真实的 `sent` 表里，是二值的、可复现的。

## 为什么只有 1.5B–8B 的小模型？

- 本地可复现：读者不用 API key 也能跑
- 成本低：一次 20 trials 几十分钟
- 结论是“机制性”的，不是“排行榜”的

前沿 API 模型是下一步，不是否定当前结果的理由。

## ASR 和策略违规有什么区别？

- **ASR**：机密有没有真的被发出去（canary 在不在 `sent` 里）
- **策略违规**：有没有发给通讯录外的人（哪怕没带机密）

两者是不同层次的伤害。只看 ASR 会把“只越权、没带机密”误判成“防住了”。

## 为什么 Llama 3.1 抵抗？

不是因为它“更安全”，而是它的模板把**工具结果包成 `ipython` 轮**，注入没有落到 user 轮上。

我们用 raw prompt 探针和模板改造（`ipython` → `user`）验证了这一点：改版后条件 ASR 从 0/5 变成 6/7。

## 三层防御是不是过度设计？

不是。每一层解决一个不同维度：

- `allowlist`：发给谁
- `content_redaction`：发了什么
- `recovery`：拦完之后还能不能继续干活

单独用任何一层都会在某个维度漏，报告 4.10 / 4.11 有数据。

## 5–20 次样本够吗？

不够精确，但足够看方向。所有结论都带 95% Wilson 区间；区间宽的地方（如 n=5）在报告里明确标注了“初步”。

## 我能用它测自己的 Agent 吗？

可以。替换 `envs/` 或加 `tasks/`，保持 oracle 和 benign check。只在**你拥有或获授权**的系统上使用。

## 和 InjecAgent / AgentDojo 的区别？

它们更偏“攻击集/环境集”；AgentRange 的重点是**测量方法**：

- 可执行 oracle 代替 LLM judge
- exposed / ASR / policy violation / utility 分开
- 防御必须同时报告 utility

## 为什么叫 AgentRange？

Range = 靶场。一个可以反复跑、结果可复现的 Agent 射击场。
