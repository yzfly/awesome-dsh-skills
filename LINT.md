<div align="center">

<a href="https://code.jiangshu.ai/awesome-dsh-skills"><img src="docs/brand/mark.svg" width="72" alt=""></a>

# dsh-skill-lint

**The DSH Skill Specification, and the linter that enforces it.**

[![CI](https://img.shields.io/github/actions/workflow/status/yzfly/dsh-skill-lint/update.yml?style=flat-square&labelColor=0c1020)](https://github.com/yzfly/awesome-dsh-skills/actions)
[![Spec 0.1](https://img.shields.io/badge/spec-0.1-7c8cff?style=flat-square&labelColor=0c1020)](SPEC.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-38d4ff?style=flat-square&labelColor=0c1020)](pyproject.toml)
[![MIT](https://img.shields.io/badge/license-MIT-c084fc?style=flat-square&labelColor=0c1020)](LICENSE)

[Specification](SPEC.md) · [规范（中文）](SPEC.zh.md) · [Back to the list](README.md)

</div>

---

A skill is a `SKILL.md` that an agent loads and follows. Most of them are written once and never checked. `dsh-skill-lint` reads a skill the way an agent would and tells you what will go wrong: a `description` the agent can't match on, a referenced script that doesn't exist, a leaked token, a `curl | sh` buried in step 4.

Zero dependencies. One file per rule ID in the [spec](SPEC.md). Works on any Agent Skills–style `SKILL.md`, not only dsh.

## Install

```bash
pip install git+https://github.com/yzfly/awesome-dsh-skills
```

## Use

```bash
dsh-skill-lint                    # scan the current directory
dsh-skill-lint skills/ my/SKILL.md
dsh-skill-lint --strict           # warnings fail too
dsh-skill-lint --format json      # machine-readable
dsh-skill-lint --min-score 75     # gate on grade B or better
```

```
A  94  skills/pdf-extract/SKILL.md  (pdf-extract)
   · DSK017  no `metadata.version` — versioning helps users track changes

D   0  skills/deploy/SKILL.md  (Best Skill!)
   ✖ DSK011:1  `name` must be 1–64 chars of lowercase letters, digits and hyphens: got 'Best Skill!'
   ✖ DSK030:7  possible embedded secret: GitHub token
   ▲ DSK031:8  dangerous shell pattern: pipe remote script into shell
   ▲ DSK013:1  `description` should say when to use the skill (e.g. "Use when the user …")

2 skills · 1 conformant · average score 47 · spec 0.1
```

Exit code is `0` when every skill is conformant (no MUST violations), `1` otherwise, `2` when nothing was found.

## In CI

```yaml
- uses: yzfly/awesome-dsh-skills@main
  with:
    path: skills/
    strict: true
```

Findings show up as inline annotations on the pull request.

## What it checks

| Area | Rules | Examples |
|:--|:--|:--|
| Layout | DSK001–003 | frontmatter present, directory matches `name`, referenced files exist |
| Frontmatter | DSK010–019 | valid keys, `name` format, `description` length and **trigger clause**, no marketing copy, semver |
| Body | DSK020–023 | non-trivial instructions, headings, ≤ 500 lines |
| Safety | DSK030–033 | embedded secrets, `rm -rf /`, `curl \| sh`, hidden-from-user instructions |
| Repository | DSK040–042 | LICENSE, README |

Scoring: `100 − 25×errors − 6×warnings − 1×infos`; any error caps it at 59. **A** ≥ 90 · **B** ≥ 75 · **C** ≥ 60 · **D** below. Full text and rationale: [SPEC.md](SPEC.md).

## Why a spec

Skills are prompts that run tools on your machine. The ecosystem has hundreds of them and no shared definition of "well-formed". This spec is deliberately small — a page — and versioned, so tools, directories and marketplaces can point at the same rules. [Awesome DSH Skills](https://code.jiangshu.ai/awesome-dsh-skills) uses it to decide what gets a ✅.

Proposals for new rules: open an issue with the rule text, level (MUST/SHOULD/MAY) and one real skill it would have caught.

## Development

```bash
python -m unittest discover -s tests -v
python -m dsh_skill_lint tests/fixtures
```

## License

The linter code is MIT; see [LICENSE-LINT](LICENSE-LINT). The list itself is CC0. Brand assets: [BRAND.md](BRAND.md).
