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


def line(e: dict) -> str:
    badge = BADGES.get(e["verified"], "")
    desc = cell(e["description"]) or "(no description)"
    star = f"{e['stars']}" if e["stars"] >= 5 else "–"
    name = e["repo"]
    return f"| [{name}](https://github.com/{name}) | {star} | {badge} | {desc} |"


TABLE_HEAD_EN = "| Repo | ⭐ | ✓ | Description |\n|:--|--:|:-:|:--|"
TABLE_HEAD_ZH = "| 仓库 | ⭐ | ✓ | 简介 |\n|:--|--:|:-:|:--|"


def render(entries: list, zh: bool) -> str:
    today = date.today().isoformat()
    total = len(entries)
    verified = sum(1 for e in entries if e["verified"] == "yes")
    by_cat: dict[str, list] = {}
    for e in entries:
        by_cat.setdefault(categorize(e), []).append(e)

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
        body.extend(line(e) for e in sorted(items, key=lambda x: -x["stars"]))

    if zh:
        header = f"""# Awesome DSH Skills [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

[English](README.md) | 中文

> [DeepSeek Harness (dsh)](https://github.com/deepseek-ai/deepseek-harness) 技能（Skill）自动发现与实测榜单。

**{total}** 个技能仓库 · **{verified}** 个通过 SKILL.md 校验 · 每日自动更新（最后更新 {today}）

🔎 **可搜索网站：{SITE}** — 按分类、star、校验状态筛选。

## 收录与校验

- 候选来自 GitHub topic（`dsh-skill` 等）与全文搜索的每日爬取，欢迎 PR 自荐（见 [CONTRIBUTING](CONTRIBUTING.md)）。
- 描述文字取自各仓库自己的 GitHub 简介，不做转载。
- ✅ = 仓库中找到 SKILL.md 且 frontmatter（name/description）合法，可被 dsh 加载；☑️ = 找到 SKILL.md 但 frontmatter 不完整；无标记 = 未在常规路径找到 SKILL.md（可能是特殊布局，欢迎 PR 修正）。
- 收录不代表安全背书：技能会驱动 agent 在你机器上执行操作，安装前请自行审查源码。

## 目录

"""
    else:
        header = f"""# Awesome DSH Skills [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

English | [中文](README.zh.md)

> Auto-discovered & verified skills for [DeepSeek Harness (dsh)](https://github.com/deepseek-ai/deepseek-harness).

**{total}** skill repos tracked · **{verified}** passed SKILL.md validation · updated daily (last: {today})

🔎 **Searchable site: {SITE}** — filter by category, stars, and verification status.

## How entries get here

- Candidates are crawled daily from GitHub topics (`dsh-skill`, …) and full-text search; PRs welcome ([CONTRIBUTING](CONTRIBUTING.md)).
- Descriptions come from each repo's own GitHub description — never copied from other lists.
- ✅ = a SKILL.md with valid frontmatter (name/description) was found, so dsh can load it; ☑️ = SKILL.md found but frontmatter incomplete; no mark = no SKILL.md found in common layouts (may be a custom layout — PRs welcome).
- A listing is not a security endorsement: skills drive an agent that acts on your machine. Review the source before installing.

## Contents

"""
    footer = f"""

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Add the `dsh-skill` topic to your repo and the daily crawl will pick it up automatically.

## Badge

Listed here? Add the badge to your README:

```markdown
[![Awesome DSH Skills]({SITE}/badge.svg)]({REPO_URL})
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

    (ROOT / "README.md").write_text(render(entries, zh=False))
    (ROOT / "README.zh.md").write_text(render(entries, zh=True))

    cat_names = {k: {"en": en, "zh": zh} for k, en, zh, _ in CATEGORIES}
    site_data = {
        "updated": date.today().isoformat(),
        "categories": cat_names,
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
            }
            for e in entries
        ],
    }
    (ROOT / "docs" / "data.json").write_text(json.dumps(site_data, ensure_ascii=False) + "\n")
    (ROOT / "docs" / "count.json").write_text(json.dumps({
        "schemaVersion": 1, "label": "dsh skills", "message": str(len(entries)), "color": "blue",
    }) + "\n")
    print(f"generated README.md / README.zh.md / docs data for {len(entries)} entries")


if __name__ == "__main__":
    main()
