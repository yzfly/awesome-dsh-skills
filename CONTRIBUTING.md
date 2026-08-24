# Contributing · 投稿指南

## 自动收录（推荐） / Automatic listing (recommended)

给你的技能仓库加上 GitHub topic **`dsh-skill`**，每日爬虫会自动发现并收录。
Add the **`dsh-skill`** topic to your repo — the daily crawl picks it up automatically.

收录后会自动校验：在仓库根目录、一级子目录或 `skills/` 目录下查找 `SKILL.md`，frontmatter 需包含 `name` 与 `description` 才能获得 ✅ 标记。

## 手动提交 / Manual submission

自动发现漏掉了？PR 修改 `data/seed_repos.txt`，一行一个 `owner/repo`。
Missed by the crawl? PR your `owner/repo` (one per line) into `data/seed_repos.txt`.

## 修正条目 / Corrections

分类、校验状态标错了？PR 修改 `data/overrides.json`：

```json
{
  "owner/repo": {
    "category": "docs-writing",
    "verified": "yes",
    "skill_files": ["path/to/SKILL.md"]
  }
}
```

`overrides.json` 优先于自动化结果，不会被每日更新覆盖。

## 注意 / Notes

- `README.md` / `README.zh.md` / `docs/data.json` 由脚本生成，请勿直接编辑（PR 只改 `data/` 下的文件）。
- 收录不构成安全背书；恶意或失效仓库会被移除。
