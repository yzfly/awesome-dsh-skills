#!/usr/bin/env python3
"""Generate README.md, README.zh.md, docs/data.json and docs/count.json
from data/skills.json. Categorization is keyword-based; data/overrides.json
can pin a category per repo."""

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORIES = [
    ("packs", "📦 Skill Packs & Curations", "📦 技能合集与精选", ["pack", "collection", "curated", "合集", "精选", "技能库", "skills-", "awesome", "manager", "管理", "list of"]),
    ("docs-writing", "📝 Docs, Writing & Office", "📝 文档、写作与办公", ["doc", "pdf", "word", "ppt", "slide", "resume", "论文", "写作", "文档", "报告", "presentation", "office", "docx", "excel", "简历", "周报", "letter"]),
    ("data-viz", "📊 Data & Visualization", "📊 数据与可视化", ["chart", "viz", "visual", "diagram", "plot", "dashboard", "数据分析", "图表", "可视化", "graph"]),
    ("coding", "💻 Coding, Review & Architecture", "💻 编码、审查与架构", ["code review", "lint", "refactor", "test", "debug", "代码", "审查", "review", "architecture", "架构", "sql", "database", "api"]),
    ("research", "🔍 Research & Knowledge", "🔍 研究与知识", ["research", "search", "调研", "检索", "rag", "knowledge", "paper", "学术", "报告生成", "arxiv", "文献"]),
    ("media", "🎨 Design & Media", "🎨 设计与多媒体", ["design", "image", "video", "banner", "logo", "图片", "视频", "海报", "设计", "photo", "audio", "音频", "tts", "asr", "字幕", "剪辑", "poster", "svg", "icon"]),
    ("automation", "🌐 Web & Automation", "🌐 网络与自动化", ["browser", "automation", "workflow", "浏览器", "自动化", "publish", "发布", "爬虫", "scrape", "抓取", "rpa"]),
    ("agents", "🤖 Agents & Orchestration", "🤖 智能体与编排", ["agent", "orchestr", "multi-agent", "subagent", "协作", "编排", "swarm", "routing"]),
    ("edu", "🎓 Education & Competitions", "🎓 教育与竞赛", ["数学建模", "竞赛", "education", "learn", "tutorial", "教学", "考试", "course", "题"]),
    ("life", "🎮 Fun & Lifestyle", "🎮 趣味与生活", ["game", "fun", "王者", "菜谱", "fortune", "星座", "娱乐", "旅行", "健康", "fitness"]),
    ("other", "🧰 Other Skills", "🧰 其他", []),
]

BADGES = {
    "yes": "✅",
    "partial": "☑️",
    "no": "",
}

SITE = "https://code.jiangshu.ai/awesome-dsh-skills"
REPO_URL = "https://github.com/yzfly/awesome-dsh-skills"


def categorize(entry: dict) -> str:
    if entry.get("category"):
        return entry["category"]
    text = f"{entry['repo']} {entry['description']} {' '.join(entry.get('topics', []))}".lower()
    for key, _en, _zh, keywords in CATEGORIES:
        if any(k in text for k in keywords):
            return key
    return "other"


def cell(text: str) -> str:
    """Make free text safe inside a markdown table cell."""
    text = re.sub(r"\s+", " ", text or "").strip()
    return text.replace("|", "\\|")


def line(e: dict, pick: bool = False) -> str:
    badge = BADGES.get(e["verified"], "")
    desc = cell(e["description"]) or "(no description)"
    star = f"{e['stars']}" if e["stars"] >= 5 else "–"
    name = e["repo"]
    mark = "✦ " if pick else ""
    return f"| {mark}[{name}](https://github.com/{name}) | {star} | {badge} | {desc} |"


TABLE_HEAD_EN = "| Repo | ⭐ | ✓ | Description |\n|:--|--:|:-:|:--|"
TABLE_HEAD_ZH = "| 仓库 | ⭐ | ✓ | 简介 |\n|:--|--:|:-:|:--|"


MARK_PATH = "M12 3.2l2.3 5.3 5.3 2.3-5.3 2.3L12 18.4l-2.3-5.3-5.3-2.3 5.3-2.3z"
FONT = "Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"


def banner(total: int, verified: int, today: str) -> str:
    """README hero — 1200x300, dark, brand gradient, live counts."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300" role="img" aria-label="Awesome DSH Skills — {total} skills, {verified} verified">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c8cff"/><stop offset=".55" stop-color="#38d4ff"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
    <radialGradient id="a1" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(160 40) scale(420)"><stop offset="0" stop-color="#7c8cff" stop-opacity=".55"/><stop offset="1" stop-color="#7c8cff" stop-opacity="0"/></radialGradient>
    <radialGradient id="a2" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1050 260) scale(460)"><stop offset="0" stop-color="#38d4ff" stop-opacity=".45"/><stop offset="1" stop-color="#38d4ff" stop-opacity="0"/></radialGradient>
    <radialGradient id="a3" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(700 -40) scale(380)"><stop offset="0" stop-color="#c084fc" stop-opacity=".4"/><stop offset="1" stop-color="#c084fc" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".05"/></pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <mask id="m"><rect width="1200" height="300" fill="url(#fade)"/></mask>
    <clipPath id="c"><rect width="1200" height="300" rx="24"/></clipPath>
  </defs>
  <g clip-path="url(#c)">
    <rect width="1200" height="300" fill="#070a12"/>
    <rect width="1200" height="300" fill="url(#a1)"/>
    <rect width="1200" height="300" fill="url(#a2)"/>
    <rect width="1200" height="300" fill="url(#a3)"/>
    <rect width="1200" height="300" fill="url(#grid)" mask="url(#m)"/>
    <rect x=".5" y=".5" width="1199" height="299" rx="23.5" fill="none" stroke="#fff" stroke-opacity=".1"/>
  </g>
  <rect x="72" y="76" width="64" height="64" rx="17" fill="url(#g)"/>
  <g transform="translate(72 76) scale(2.6667)"><path d="{MARK_PATH}" fill="#fff"/></g>
  <text x="160" y="126" font-family="{FONT}" font-size="54" font-weight="800" letter-spacing="-2.2" fill="#eef1f8">Awesome <tspan fill="url(#g)">DSH</tspan> Skills</text>
  <text x="74" y="184" font-family="{FONT}" font-size="19" fill="#aab3c7">Auto-discovered, verified and categorized skills for DeepSeek Harness.</text>
  <g font-family="{FONT}" font-size="13" font-weight="600" letter-spacing="1.2">
    <rect x="72" y="214" width="150" height="40" rx="10" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".1"/>
    <text x="88" y="240" fill="#eef1f8" font-size="18" font-weight="800" letter-spacing="-.5">{total}</text>
    <text x="{88 + 12 * len(str(total)) + 6}" y="239" fill="#6f7a93">SKILLS</text>
    <rect x="234" y="214" width="166" height="40" rx="10" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".1"/>
    <text x="250" y="240" fill="#34d399" font-size="18" font-weight="800" letter-spacing="-.5">{verified}</text>
    <text x="{250 + 12 * len(str(verified)) + 6}" y="239" fill="#6f7a93">VERIFIED</text>
    <rect x="412" y="214" width="200" height="40" rx="10" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".1"/>
    <text x="428" y="239" fill="#6f7a93">UPDATED</text>
    <text x="502" y="240" fill="#eef1f8" font-size="15" font-weight="700" letter-spacing="0">{today}</text>
  </g>
  <text x="1128" y="246" text-anchor="end" font-family="{FONT}" font-size="13" font-weight="600" letter-spacing="1.2" fill="#6f7a93">code.jiangshu.ai/awesome-dsh-skills</text>
</svg>
"""


def load_edition() -> dict | None:
    p = ROOT / "data" / "edition.json"
    return json.loads(p.read_text()) if p.exists() else None


def render(entries: list, zh: bool, edition: dict | None = None) -> str:
    today = date.today().isoformat()
    total = len(entries)
    verified = sum(1 for e in entries if e["verified"] == "yes")
    by_cat: dict[str, list] = {}
    for e in entries:
        by_cat.setdefault(categorize(e), []).append(e)

    picks = set(edition["picks"]) if edition else set()
    edition_en = edition_zh = ""
    if edition:
        edition_en = f"""
✦ **[{edition['title']}]({edition['page']})** — {len(picks)} skills read and reviewed one by one, with verdicts. Picks are marked ✦ below.
"""
        edition_zh = f"""
✦ **[{edition['title']}]({edition['page']})** — {len(picks)} 个技能逐个审读并给出点评。入选项在下方以 ✦ 标记。
"""

    toc, body = [], []
    for key, en_name, zh_name, _kw in CATEGORIES:
        items = by_cat.get(key)
        if not items:
            continue
        name = zh_name if zh else en_name
        # GitHub anchors: emoji stripped but leave a leading "-", "&" and
        # extra spaces collapse to "-" per space
        anchor = re.sub(r"[^\w一-鿿 -]", "", name).lower().replace(" ", "-")
        toc.append(f"- [{name}](#{anchor}) ({len(items)})")
        body.append(f"\n### {name}\n")
        body.append(TABLE_HEAD_ZH if zh else TABLE_HEAD_EN)
        body.extend(line(e, e["repo"] in picks) for e in sorted(items, key=lambda x: -x["stars"]))

    if zh:
        header = f"""<div align="center">

<a href="{SITE}"><img src="docs/brand/banner.svg" alt="Awesome DSH Skills" width="100%"></a>

<br>

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Skills](https://img.shields.io/endpoint?url={SITE}/count.json&style=flat-square&color=7c8cff&labelColor=0c1020)]({SITE})
[![Daily update](https://img.shields.io/github/actions/workflow/status/yzfly/awesome-dsh-skills/update.yml?style=flat-square&label=daily%20update&labelColor=0c1020)](https://github.com/yzfly/awesome-dsh-skills/actions)
[![License CC0](https://img.shields.io/badge/license-CC0--1.0-38d4ff?style=flat-square&labelColor=0c1020)](LICENSE)

[English](README.md) · **中文**

</div>

> [DeepSeek Harness (dsh)](https://github.com/deepseek-ai/deepseek-harness) 技能（Skill）自动发现与实测榜单。

**{total}** 个技能仓库 · **{verified}** 个通过 SKILL.md 校验 · 每日自动更新（最后更新 {today}）

🔎 **可搜索网站：{SITE}** — 按分类、star、校验状态筛选。
{edition_zh}
## 收录与校验

- 候选来自 GitHub topic（`dsh-skill` 等）与全文搜索的每日爬取，欢迎 PR 自荐（见 [CONTRIBUTING](CONTRIBUTING.md)）。
- 描述文字取自各仓库自己的 GitHub 简介，不做转载。
- ✅ = 仓库中找到 SKILL.md 且 frontmatter（name/description）合法，可被 dsh 加载；☑️ = 找到 SKILL.md 但 frontmatter 不完整；无标记 = 未在常规路径找到 SKILL.md（可能是特殊布局，欢迎 PR 修正）。
- 想要更强的质量信号？用 [`dsh-skill-lint`](LINT.md) 按 [DSH Skill 规范](SPEC.zh.md) 检查你的技能——它会发现缺失的触发语、失效引用、泄露的密钥和不安全的 shell 模式。
- 收录不代表安全背书：技能会驱动 agent 在你机器上执行操作，安装前请自行审查源码。

## 目录

"""
    else:
        header = f"""<div align="center">

<a href="{SITE}"><img src="docs/brand/banner.svg" alt="Awesome DSH Skills" width="100%"></a>

<br>

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Skills](https://img.shields.io/endpoint?url={SITE}/count.json&style=flat-square&color=7c8cff&labelColor=0c1020)]({SITE})
[![Daily update](https://img.shields.io/github/actions/workflow/status/yzfly/awesome-dsh-skills/update.yml?style=flat-square&label=daily%20update&labelColor=0c1020)](https://github.com/yzfly/awesome-dsh-skills/actions)
[![License CC0](https://img.shields.io/badge/license-CC0--1.0-38d4ff?style=flat-square&labelColor=0c1020)](LICENSE)

**English** · [中文](README.zh.md)

</div>

> Auto-discovered & verified skills for [DeepSeek Harness (dsh)](https://github.com/deepseek-ai/deepseek-harness).

**{total}** skill repos tracked · **{verified}** passed SKILL.md validation · updated daily (last: {today})

🔎 **Searchable site: {SITE}** — filter by category, stars, and verification status.
{edition_en}
## How entries get here

- Candidates are crawled daily from GitHub topics (`dsh-skill`, …) and full-text search; PRs welcome ([CONTRIBUTING](CONTRIBUTING.md)).
- Descriptions come from each repo's own GitHub description — never copied from other lists.
- ✅ = a SKILL.md with valid frontmatter (name/description) was found, so dsh can load it; ☑️ = SKILL.md found but frontmatter incomplete; no mark = no SKILL.md found in common layouts (may be a custom layout — PRs welcome).
- Want a stronger signal? Check your skill against the [DSH Skill Specification](SPEC.md) with [`dsh-skill-lint`](LINT.md) — it catches missing trigger clauses, broken references, leaked secrets and unsafe shell patterns.
- A listing is not a security endorsement: skills drive an agent that acts on your machine. Review the source before installing.

## Contents

"""
    footer = f"""

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Add the `dsh-skill` topic to your repo and the daily crawl will pick it up automatically.

## Badge

Listed here? Add the badge to your README — [![Listed on Awesome DSH Skills]({SITE}/badge.svg)]({REPO_URL})

```markdown
[![Listed on Awesome DSH Skills]({SITE}/badge.svg)]({REPO_URL})
```

Brand assets and usage: [BRAND.md](BRAND.md).

## Specification

The ✅ mark is the core check of the [DSH Skill Specification](SPEC.md) (frontmatter with valid `name` and `description`). Run the full linter on your own skill (docs: [LINT.md](LINT.md)):

```bash
pip install git+https://github.com/yzfly/awesome-dsh-skills && dsh-skill-lint
```

## License

[CC0-1.0](LICENSE)
"""
    return header + "\n".join(toc) + "\n" + "\n".join(body) + footer


def main() -> None:
    entries = json.loads((ROOT / "data" / "skills.json").read_text())
    overrides_path = ROOT / "data" / "overrides.json"
    overrides = json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    for e in entries:
        e.update(overrides.get(e["repo"], {}))
    entries = [e for e in entries if not e.get("hidden")]

    verified = sum(1 for e in entries if e["verified"] == "yes")
    (ROOT / "docs" / "brand" / "banner.svg").write_text(banner(len(entries), verified, date.today().isoformat()))
    edition = load_edition()
    picks = set(edition["picks"]) if edition else set()
    (ROOT / "README.md").write_text(render(entries, zh=False, edition=edition))
    (ROOT / "README.zh.md").write_text(render(entries, zh=True, edition=edition))

    cat_names = {k: {"en": en, "zh": zh} for k, en, zh, _ in CATEGORIES}
    site_data = {
        "updated": date.today().isoformat(),
        "categories": cat_names,
        "edition": {"id": edition["id"], "title": edition["title"], "url": f"{REPO_URL}/blob/main/{edition['page']}"} if edition else None,
        "skills": [
            {
                "repo": e["repo"],
                "description": e["description"],
                "stars": e["stars"],
                "verified": e["verified"],
                "category": categorize(e),
                "topics": e.get("topics", []),
                "created_at": e.get("created_at", ""),
                "pushed_at": e.get("pushed_at", ""),
                "pick": e["repo"] in picks,
            }
            for e in entries
        ],
    }
    (ROOT / "docs" / "data.json").write_text(json.dumps(site_data, ensure_ascii=False) + "\n")
    (ROOT / "docs" / "count.json").write_text(json.dumps({
        "schemaVersion": 1, "label": "dsh skills", "message": str(len(entries)), "color": "7c8cff",
    }) + "\n")
    print(f"generated README.md / README.zh.md / docs data for {len(entries)} entries")


if __name__ == "__main__":
    main()
