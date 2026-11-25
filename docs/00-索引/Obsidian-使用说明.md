# Obsidian 使用说明

## 为什么用 Obsidian

- **本地 Markdown**：GitHub 能直接渲染，不锁定格式，换工具不丢数据。
- **双链 + 图谱**：知识之间能连起来，而不是一堆孤立笔记。
- **Dataview**：可以用查询把实验记录自动汇总成表。
- **和代码同仓库**：`docs/` 就是 vault，提交即备份。

## 第一次打开

1. 下载 <https://obsidian.md>
2. 选 “Open folder as vault”
3. 选择 `E:\agenttest\agentrange\docs`
4. 信任作者并启用插件

## 推荐设置

- 文件与链接 → 附件默认位置：`_attachments`
- 文件与链接 → 新建笔记位置：当前文件夹
- 编辑器 → 默认视图：阅读视图（写作时切回编辑）

## 推荐插件

| 插件 | 用途 |
|---|---|
| Dataview | 查询实验记录、任务清单 |
| Templater | 自动套用模板 |
| Excalidraw | 画攻击链路图 |
| Git（可选） | 在 Obsidian 里提交 |

## 命名约定

- 课程：`第N课-<主题>.md`
- 论文：`论文-<短名>.md`
- 实验：`YYYY-MM-DD-<主题>.md`
- 决策：`ADR-NNN-<主题>.md`
- 日志：`YYYY-Www.md`

## 和 Git 的关系

- `.obsidian/workspace.json` 记录窗口布局，**不提交**（已在 `.gitignore`）。
- 其他 `.obsidian/` 配置可以提交，方便换机。
- 私人内容放 `docs/_private/`，已在 `.gitignore` 中。

## 注意

笔记是为项目服务的。不要花三天搭一套完美的笔记系统——先写，再整理。
