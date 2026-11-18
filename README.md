# Skills

按平台整理可复用的 AI 编程助手技能，保留各平台原生的目录结构、元数据和使用方式。

## 平台目录

| 平台 | 目录 | 状态 |
| --- | --- | --- |
| Codex | [`codex/`](codex/) | 已收录技能 |
| Claude | `claude/` | 后续收录时创建 |
| Cursor | `cursor/` | 后续收录时创建 |

各平台采用 `<平台>/<技能名>/` 组织。相同能力在不同平台的实现分别维护，不默认它们的配置格式或调用方式可以互换。

## 已收录技能

| 平台 | 技能 | 功能 |
| --- | --- | --- |
| Codex | [`model-architecture-atlas`](codex/model-architecture-atlas/SKILL.md) | 结合模型论文与源码生成中文离线交互 HTML，包含总架构、逐节点维度与算子、输入输出、训练推理和创新问题分析。 |

## 使用 Codex 技能

将所需技能的整个文件夹复制到 `$CODEX_HOME/skills/`；未设置 `CODEX_HOME` 时，使用 `~/.codex/skills/`。保留 `assets/`、`references/`、`scripts/` 和 `agents/` 等随附资源。

例如复制 `codex/model-architecture-atlas/` 后，在支持技能的 Codex 会话中使用：

```text
使用 $model-architecture-atlas，结合下面的论文和代码，制作这个模型的中文离线交互学习图谱。
论文：……
代码：……
```

完整的布局与交互参考见 [`assets/reference.html`](codex/model-architecture-atlas/assets/reference.html)，下载到本地后用浏览器打开。它使用教学示例展示样式；实际模型内容由提供的论文、代码与配置决定。

## 收录约定

- 技能文件夹以小写英文和连字符命名，遵循对应平台格式。
- 技能及随附资源应自包含，不依赖作者电脑上的绝对路径或某次聊天记录。
- 附带脚本需要说明运行方式与依赖；提交前执行相应校验。
- 不提交凭据、个人环境配置、依赖缓存或测试临时文件。
- 新增平台或技能时同步更新本页目录与索引。
