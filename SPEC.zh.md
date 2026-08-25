# DSH Skill 规范

**版本 0.1 · 2026-08-25 · 状态：草案**

本规范定义一个格式正确、可被加载、可信任的 [DeepSeek Harness (dsh)](https://github.com/deepseek-ai/deepseek-harness) 技能应该是什么样子。它与 Claude Code、Codex、OpenCode 通用的 Agent Skills 约定（`SKILL.md` + YAML frontmatter）兼容——符合本规范的技能在各处都能用。

MUST（必须）、SHOULD（应当）、MAY（可以）按 RFC 2119 理解。每条要求有规则编号，[`dsh-skill-lint`](README.md) 逐条检查。

English: [SPEC.md](SPEC.md)

---

## 1. 目录布局

技能是一个包含 `SKILL.md` 的目录，目录内其他内容都属于该技能。

```
my-skill/
├── SKILL.md          # 必需 — frontmatter + 指令
├── references/       # 可选 — 长篇资料，按需加载
├── scripts/          # 可选 — 可执行辅助脚本
└── assets/           # 可选 — 模板、图片
```

| 编号 | 级别 | 规则 |
|:--|:--|:--|
| DSK001 | MUST | `SKILL.md` 存在、UTF-8 编码、以 `---` 包围的 YAML frontmatter 开头。 |
| DSK002 | SHOULD | 目录名与 `name` 一致。仓库根目录即技能（根 `SKILL.md`）的情况豁免。 |
| DSK003 | SHOULD | `SKILL.md` 中以相对路径引用的文件（`scripts/run.py`、`references/api.md`）真实存在。 |

## 2. Frontmatter

```yaml
---
name: pdf-extract
description: 从 PDF 提取文本与表格为 Markdown。当用户分享 PDF 或要求阅读、总结、转换 PDF 时使用。
license: MIT
metadata:
  version: "1.2.0"
  author: yzfly
allowed-tools: Read, Bash
---
```

| 编号 | 级别 | 规则 |
|:--|:--|:--|
| DSK010 | MUST | frontmatter 是合法 YAML，只使用下列键（`metadata` 下可自定义）。 |
| DSK011 | MUST | `name` 存在，1–64 字符，仅小写字母、数字、连字符（`^[a-z0-9]+(-[a-z0-9]+)*$`）。 |
| DSK012 | MUST | `description` 存在，20–1024 字符。 |
| DSK013 | SHOULD | `description` 说明**何时**使用（触发语，如 "Use when…"、"适用于…"、"当用户…"）。agent 靠这个匹配。 |
| DSK014 | SHOULD | `description` 面向 agent 而非营销：不用感叹号，不纯 emoji，不写 "best"/"ultimate"/"最强"。 |
| DSK015 | SHOULD | `name` 具体：不是 `skill`、`test`、`demo`、`example`、`new-skill`。 |
| DSK016 | MAY | `license` — SPDX 标识。缺省时仓库根目录应有 `LICENSE`（DSK040）。 |
| DSK017 | MAY | `metadata.version` — 语义化版本。 |
| DSK018 | MAY | `allowed-tools` — 逗号分隔的工具名。若存在必须非空。 |
| DSK019 | MAY | `argument-hint`、`user-invocable`、`disable-model-invocation` — 按 Agent Skills 约定。 |

已识别的顶层键：`name`、`description`、`license`、`metadata`、`allowed-tools`、`argument-hint`、`user-invocable`、`disable-model-invocation`、`version`、`compatibility`。未知键给警告（DSK010w）而非错误，便于规范演进。

## 3. 正文

frontmatter 之后的 Markdown 是技能激活后 agent 读取的指令。

| 编号 | 级别 | 规则 |
|:--|:--|:--|
| DSK020 | MUST | 正文非空：至少 200 字符的指令。 |
| DSK021 | SHOULD | 正文使用标题（`#`、`##`）组织步骤。 |
| DSK022 | SHOULD | 正文不超过 500 行。长资料放到 `references/` 并链接——渐进披露节省上下文。 |
| DSK023 | SHOULD | 正文不是仅把 `description` 原样重复一遍。 |

## 4. 安全

技能驱动 agent 在用户机器上执行操作。被收录的技能不得让用户意外。

| 编号 | 级别 | 规则 |
|:--|:--|:--|
| DSK030 | MUST | 不内嵌密钥：API key、token、私钥（`sk-…`、`ghp_…`、`AKIA…`、`-----BEGIN … PRIVATE KEY-----`）。 |
| DSK031 | SHOULD | 指令中没有破坏性或不透明的 shell 模式：`rm -rf /`、`rm -rf ~`、`curl … \| sh`、`wget … \| bash`、`chmod -R 777`、fork 炸弹。确需下载执行代码时应固定版本并明示。 |
| DSK032 | SHOULD | 网络目标可见：调用的 URL 以明文出现，不靠字符串拼接。 |
| DSK033 | SHOULD | 没有要求关闭安全机制、对用户隐藏操作、忽略用户确认的指令。 |

## 5. 仓库

| 编号 | 级别 | 规则 |
|:--|:--|:--|
| DSK040 | SHOULD | 仓库根目录有 `LICENSE`（或每个技能声明 `license`）。 |
| DSK041 | SHOULD | 仓库根目录有 `README.md`。 |
| DSK042 | MAY | 仓库带 `dsh-skill` GitHub topic 以便被发现。 |

## 6. 符合性

- **符合（Conformant）** — 没有 MUST 违规。
- **分数** — `100 − 25×错误 − 6×警告 − 1×提示`，最低 0。任一 MUST 违规将分数封顶为 59。等级：**A** ≥ 90 · **B** ≥ 75 · **C** ≥ 60 · **D** 其余。
- [Awesome DSH Skills](https://code.jiangshu.ai/awesome-dsh-skills) 榜单在仓库至少有一个符合规范的技能时标记 ✅。

## 7. 变更记录

- **0.1**（2026-08-25）— 首个草案。
