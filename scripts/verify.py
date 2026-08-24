#!/usr/bin/env python3
"""Verify candidate repos actually ship loadable skills.

For each repo in data/candidates.json, look for SKILL.md files (repo root,
one directory level down, and inside a skills/ folder), fetch them, and
check the frontmatter parses with the required `name` and `description`
fields. Results land in data/skills.json:

  verified: "yes"     - at least one SKILL.md with valid frontmatter
  verified: "partial" - SKILL.md found but frontmatter incomplete
  verified: "no"      - no SKILL.md located (may still be a skill pack
                        with a layout we don't scan; see manual overrides)

data/overrides.json can pin category / verified / note per repo and is
never touched by automation.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
if not TOKEN:
    sys.exit("GITHUB_TOKEN not set")

API_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "awesome-dsh-skills-verifier",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def api(url: str):
    req = urllib.request.Request(url, headers=API_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            time.sleep(30)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.load(resp)
            except Exception:
                return None
        return None
    except Exception:
        return None


def raw(repo: str, branch: str, path: str) -> str | None:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": API_HEADERS["User-Agent"]})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read(65536).decode("utf-8", "ignore")
    except Exception:
        return None


def frontmatter_ok(text: str) -> bool:
    m = FRONTMATTER_RE.search(text.lstrip("﻿"))
    if not m:
        return False
    block = m.group(1)
    return bool(re.search(r"^name\s*:\s*\S", block, re.M)) and bool(
        re.search(r"^description\s*:\s*\S", block, re.M)
    )


def find_skill_files(repo: str, branch: str) -> list[str]:
    """Return repo-relative paths of SKILL.md files, scanning at most ~3 API calls."""
    listing = api(f"https://api.github.com/repos/{repo}/contents/?ref={branch}")
    if not isinstance(listing, list):
        return []
    names = {item["name"]: item for item in listing}
    found = []
    if "SKILL.md" in names:
        found.append("SKILL.md")

    # scan likely skill dirs: skills/, or dirs whose name mentions skill,
    # else (for dedicated skill repos) the first few top-level dirs
    dirs = [i["name"] for i in listing if i["type"] == "dir" and not i["name"].startswith(".")]
    likely = [d for d in dirs if "skill" in d.lower()] or dirs[:3]
    for d in likely[:3]:
        sub = api(f"https://api.github.com/repos/{repo}/contents/{d}?ref={branch}")
        if not isinstance(sub, list):
            continue
        subnames = {i["name"]: i for i in sub}
        if "SKILL.md" in subnames:
            found.append(f"{d}/SKILL.md")
        for i in sub:
            if i["type"] == "dir" and len(found) < 8:
                sub2 = api(f"https://api.github.com/repos/{repo}/contents/{i['path']}?ref={branch}")
                if isinstance(sub2, list) and any(x["name"] == "SKILL.md" for x in sub2):
                    found.append(f"{i['path']}/SKILL.md")
        if found:
            break
    return found


def main() -> None:
    candidates = json.loads((ROOT / "data" / "candidates.json").read_text())
    overrides_path = ROOT / "data" / "overrides.json"
    overrides = json.loads(overrides_path.read_text()) if overrides_path.exists() else {}

    results = []
    for i, cand in enumerate(candidates):
        repo, branch = cand["repo"], cand["default_branch"]
        entry = dict(cand)
        ov = overrides.get(repo, {})
        if "verified" in ov:
            entry["verified"] = ov["verified"]
            entry["skill_files"] = ov.get("skill_files", [])
        else:
            files = find_skill_files(repo, branch)
            status = "no"
            if files:
                text = raw(repo, branch, files[0])
                status = "yes" if text and frontmatter_ok(text) else "partial"
            entry["verified"] = status
            entry["skill_files"] = files
        entry.update({k: v for k, v in ov.items() if k not in ("verified", "skill_files")})
        results.append(entry)
        if i % 20 == 0:
            print(f"  {i}/{len(candidates)} {repo} -> {entry['verified']}")
        time.sleep(0.3)

    path = ROOT / "data" / "skills.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    counts = {}
    for r in results:
        counts[r["verified"]] = counts.get(r["verified"], 0) + 1
    print(f"wrote {len(results)} entries -> {path} | verified: {counts}")


if __name__ == "__main__":
    main()
