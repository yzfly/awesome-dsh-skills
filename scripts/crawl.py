#!/usr/bin/env python3
"""Discover DeepSeek Harness (dsh) skill repos on GitHub.

Merges several search strategies, filters for relevance, and writes
data/candidates.json. Descriptions always come from each repo's own
GitHub metadata, never from third-party lists.

Requires: GITHUB_TOKEN (or GH_TOKEN) env var.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
if not TOKEN:
    sys.exit("GITHUB_TOKEN not set")

API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "awesome-dsh-skills-crawler",
}

TOPIC_QUERIES = [
    "topic:dsh-skill",
    "topic:dsh-skills",
    "topic:deepseek-harness-skill",
    "topic:agent-skill topic:deepseek-harness",
    "topic:agent-skills topic:deepseek-harness",
    "topic:skill topic:deepseek-harness",
]

TEXT_QUERIES = [
    "dsh skill in:name,description",
    '"deepseek harness" skill in:description',
    '"deepseek-harness" skill in:name,description',
]

RELEVANT_TOPICS = {"dsh-skill", "dsh-skills", "deepseek-harness-skill"}
DSH_RE = re.compile(r"\b(dsh|deepseek[ -]?harness)\b", re.I)
SKILL_RE = re.compile(r"skill|技能", re.I)
EXCLUDE_REPOS = {"deepseek-ai/deepseek-harness", "yzfly/awesome-dsh-skills"}


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < 2:  # rate limited
                time.sleep(30)
                continue
            raise
    return {}


def search(query: str, pages: int = 3) -> list:
    items = []
    for page in range(1, pages + 1):
        q = urllib.parse.quote(query, safe="")
        data = get(f"{API}/search/repositories?q={q}&sort=stars&order=desc&per_page=100&page={page}")
        batch = data.get("items", [])
        items.extend(batch)
        if len(batch) < 100:
            break
        time.sleep(3)
    return items


def relevant(repo: dict, from_topic_query: bool) -> bool:
    if repo["full_name"] in EXCLUDE_REPOS or repo.get("fork") or repo.get("archived"):
        return False
    topics = set(repo.get("topics") or [])
    if topics & RELEVANT_TOPICS or from_topic_query:
        return True
    text = f"{repo['name']} {repo.get('description') or ''}"
    return bool(DSH_RE.search(text) and SKILL_RE.search(text))


def main() -> None:
    seen: dict[str, dict] = {}
    for query in TOPIC_QUERIES + TEXT_QUERIES:
        from_topic = query in TOPIC_QUERIES
        for repo in search(query):
            if repo["full_name"] in seen or not relevant(repo, from_topic):
                continue
            seen[repo["full_name"]] = {
                "repo": repo["full_name"],
                "description": (repo.get("description") or "").strip(),
                "stars": repo["stargazers_count"],
                "topics": repo.get("topics") or [],
                "default_branch": repo.get("default_branch", "main"),
                "created_at": repo.get("created_at", ""),
                "pushed_at": repo.get("pushed_at", ""),
                "homepage": repo.get("homepage") or "",
                "license": (repo.get("license") or {}).get("spdx_id") or "",
            }
        time.sleep(3)

    # extra seed repos listed one per line (community submissions / known skills)
    seeds = ROOT / "data" / "seed_repos.txt"
    if seeds.exists():
        for line in seeds.read_text().splitlines():
            full = line.strip()
            if not full or full.startswith("#") or full in seen:
                continue
            try:
                repo = get(f"{API}/repos/{full}")
            except urllib.error.HTTPError:
                continue
            if repo.get("full_name") and not repo.get("archived"):
                seen[repo["full_name"]] = {
                    "repo": repo["full_name"],
                    "description": (repo.get("description") or "").strip(),
                    "stars": repo["stargazers_count"],
                    "topics": repo.get("topics") or [],
                    "default_branch": repo.get("default_branch", "main"),
                    "created_at": repo.get("created_at", ""),
                    "pushed_at": repo.get("pushed_at", ""),
                    "homepage": repo.get("homepage") or "",
                    "license": (repo.get("license") or {}).get("spdx_id") or "",
                }
            time.sleep(0.5)

    out = sorted(seen.values(), key=lambda r: -r["stars"])
    path = ROOT / "data" / "candidates.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {len(out)} candidates -> {path}")


if __name__ == "__main__":
    main()
