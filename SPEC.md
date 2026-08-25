# DSH Skill Specification

**Version 0.1 · 2026-08-25 · Status: Draft**

This document defines what a well-formed, loadable and trustworthy skill for [DeepSeek Harness (dsh)](https://github.com/deepseek-ai/deepseek-harness) looks like. It is compatible with the Agent Skills convention (`SKILL.md` with YAML frontmatter) used across Claude Code, Codex and OpenCode, so a skill that conforms here works everywhere.

The key words MUST, SHOULD and MAY are to be interpreted as described in RFC 2119. Every requirement has a rule ID; [`dsh-skill-lint`](README.md) checks each one.

中文版见 [SPEC.zh.md](SPEC.zh.md)。

---

## 1. Layout

A skill is a directory containing a `SKILL.md` file. Anything else in the directory belongs to the skill.

```
my-skill/
├── SKILL.md          # required — frontmatter + instructions
├── references/       # optional — long material, loaded on demand
├── scripts/          # optional — executable helpers
└── assets/           # optional — templates, images
```

| ID | Level | Rule |
|:--|:--|:--|
| DSK001 | MUST | `SKILL.md` exists, is UTF-8, and starts with a YAML frontmatter block delimited by `---` lines. |
| DSK002 | SHOULD | The directory name equals the skill `name`. A repo whose root is the skill (root `SKILL.md`) is exempt. |
| DSK003 | SHOULD | Files referenced from `SKILL.md` by relative path (`scripts/run.py`, `references/api.md`) exist. |

## 2. Frontmatter

```yaml
---
name: pdf-extract
description: Extract text and tables from PDF files into Markdown. Use when the user shares a PDF or asks to read, summarize or convert one.
license: MIT
metadata:
  version: "1.2.0"
  author: yzfly
allowed-tools: Read, Bash
---
```

| ID | Level | Rule |
|:--|:--|:--|
| DSK010 | MUST | Frontmatter is valid YAML using only the keys below plus any under `metadata`. |
| DSK011 | MUST | `name` is present, 1–64 characters, lowercase letters, digits and hyphens only (`^[a-z0-9]+(-[a-z0-9]+)*$`). |
| DSK012 | MUST | `description` is present and 20–1024 characters. |
| DSK013 | SHOULD | `description` states **when** to use the skill (a trigger clause such as "Use when…", "Triggers when…", "适用于…", "当用户…"). This is what the agent matches on. |
| DSK014 | SHOULD | `description` is written for the agent, not marketing: no exclamation marks, no emoji-only, no "best"/"ultimate". |
| DSK015 | SHOULD | `name` is specific: not `skill`, `test`, `demo`, `example`, `new-skill`. |
| DSK016 | MAY | `license` — an SPDX identifier. If absent, a `LICENSE` file SHOULD exist at the repo root (DSK040). |
| DSK017 | MAY | `metadata.version` — semantic version string. |
| DSK018 | MAY | `allowed-tools` — comma-separated tool names the skill needs. If present, MUST be non-empty. |
| DSK019 | MAY | `argument-hint`, `user-invocable`, `disable-model-invocation` — booleans/strings per Agent Skills convention. |

Recognised top-level keys: `name`, `description`, `license`, `metadata`, `allowed-tools`, `argument-hint`, `user-invocable`, `disable-model-invocation`, `version`, `compatibility`. Unknown keys produce a warning (DSK010w), not an error, so the spec can grow.

## 3. Body

The Markdown after the frontmatter is the instruction the agent reads once the skill is activated.

| ID | Level | Rule |
|:--|:--|:--|
| DSK020 | MUST | Body is non-empty: at least 200 characters of instruction. |
| DSK021 | SHOULD | Body uses headings (`#`, `##`) to structure steps. |
| DSK022 | SHOULD | Body stays under 500 lines. Move long reference material to `references/` and link it — progressive disclosure keeps context cheap. |
| DSK023 | SHOULD | Body does not repeat the frontmatter `description` verbatim as its only content. |

## 4. Safety

Skills drive an agent that acts on the user's machine. A listed skill MUST NOT surprise the user.

| ID | Level | Rule |
|:--|:--|:--|
| DSK030 | MUST | No embedded secrets: API keys, tokens, private keys (`sk-…`, `ghp_…`, `AKIA…`, `-----BEGIN … PRIVATE KEY-----`). |
| DSK031 | SHOULD | No destructive or opaque shell patterns in instructions: `rm -rf /`, `rm -rf ~`, `curl … \| sh`, `wget … \| bash`, `chmod -R 777`, `:(){ :\|:& };:`. If a skill genuinely needs to download and run code, it SHOULD pin a version and say so. |
| DSK032 | SHOULD | Network destinations are visible: URLs the skill calls appear in plain text, not built from string fragments. |
| DSK033 | SHOULD | No instruction to disable safety, hide actions from the user, or ignore the user's confirmation. |

## 5. Repository

| ID | Level | Rule |
|:--|:--|:--|
| DSK040 | SHOULD | Repository root has a `LICENSE` file (or every skill declares `license`). |
| DSK041 | SHOULD | Repository root has a `README.md`. |
| DSK042 | MAY | Repository carries the `dsh-skill` GitHub topic so it can be discovered. |

## 6. Conformance

- **Conformant** — no MUST violations.
- **Score** — `100 − 25×errors − 6×warnings − 1×infos`, floor 0. Any MUST violation caps the score at 59. Grades: **A** ≥ 90 · **B** ≥ 75 · **C** ≥ 60 · **D** below.
- The [Awesome DSH Skills](https://code.jiangshu.ai/awesome-dsh-skills) listing marks a repo ✅ when at least one skill is conformant.

## 7. Changelog

- **0.1** (2026-08-25) — initial draft.
