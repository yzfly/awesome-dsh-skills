"""Rule engine for the DSH Skill Specification 0.1."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import frontmatter as fm

ERROR, WARN, INFO = "error", "warning", "info"
WEIGHTS = {ERROR: 25, WARN: 6, INFO: 1}

KNOWN_KEYS = {
    "name", "description", "license", "metadata", "allowed-tools", "argument-hint",
    "user-invocable", "disable-model-invocation", "version", "compatibility",
}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
GENERIC_NAMES = {"skill", "skills", "test", "demo", "example", "new-skill", "my-skill", "untitled"}
TRIGGER_RE = re.compile(
    r"\b(use|used|useful|trigger|triggers|activate|invoke|apply|applies|helpful)\b[^.\n]{0,40}\b(when|whenever|for|if|to)\b"
    r"|\bwhen (the )?user\b|\bwhen asked\b|适用|当用户|用于|使用场景|触发|在.{0,12}时使用|需要.{0,20}时",
    re.I,
)
HYPE_RE = re.compile(r"!{1,}|\b(best|ultimate|revolutionary|game[- ]changing|world[- ]class)\b|最强|史上|神器|终极", re.I)
SEMVER_RE = re.compile(r"^v?\d+(\.\d+){1,3}([-+][0-9A-Za-z.-]+)?$")
SECRET_RES = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}"), "OpenAI-style API key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}"), "GitHub fine-grained token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "Google API key"),
]
DANGER_RES = [
    (re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+(/|~|\$HOME|\*)(\s|$|/\*)"), "recursive delete of / or home"),
    (re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b"), "pipe remote script into shell"),
    (re.compile(r"\bchmod\s+-R\s+777\b"), "chmod -R 777"),
    (re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"), "fork bomb"),
    (re.compile(r"\bmkfs\.|\bdd\s+if=.*of=/dev/(sd|nvme|disk)"), "disk overwrite"),
]
EVASION_RE = re.compile(
    r"(do not|don'?t|never)\s+(tell|inform|show|notify|warn|alert)\s+(the\s+)?user"
    r"|(do not|don'?t|never)\s+ask\s+(the\s+)?user\s+(for\s+)?(permission|confirmation|consent|approval|before)"
    r"|without\s+(the\s+)?user'?s?\s+(consent|confirmation|knowledge|approval|permission)"
    r"|ignore\s+(all\s+)?(previous|prior|safety|system)\s+(instructions|rules|guidelines)|disable\s+(safety|guardrails|sandbox)"
    r"|不要(告诉|通知|提醒)用户|未经用户(同意|确认)|绕过(安全|确认|权限)",
    re.I,
)
REF_RE = re.compile(r"(?<![\w/:.])((?:scripts|references|assets|templates|examples|docs|bin|lib|src)/[\w./-]+)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


@dataclass
class Finding:
    rule: str
    level: str
    message: str
    path: str
    line: int | None = None

    def as_dict(self) -> dict:
        return {"rule": self.rule, "level": self.level, "message": self.message, "path": self.path, "line": self.line}


@dataclass
class Report:
    path: str
    name: str | None = None
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f.level == ERROR)

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.level == WARN)

    @property
    def infos(self) -> int:
        return sum(1 for f in self.findings if f.level == INFO)

    @property
    def score(self) -> int:
        s = max(0, 100 - sum(WEIGHTS[f.level] for f in self.findings))
        return min(s, 59) if self.errors else s

    @property
    def grade(self) -> str:
        s = self.score
        return "A" if s >= 90 else "B" if s >= 75 else "C" if s >= 60 else "D"

    @property
    def conformant(self) -> bool:
        return self.errors == 0

    def as_dict(self) -> dict:
        return {
            "path": self.path, "name": self.name, "score": self.score, "grade": self.grade,
            "conformant": self.conformant, "errors": self.errors, "warnings": self.warnings,
            "infos": self.infos, "findings": [f.as_dict() for f in self.findings],
        }


def _line_of(text: str, pattern: re.Pattern) -> int | None:
    m = pattern.search(text)
    return text.count("\n", 0, m.start()) + 1 if m else None


def _repo_root(skill_dir: Path) -> Path:
    p = skill_dir.resolve()
    for cand in [p, *p.parents]:
        if (cand / ".git").exists():
            return cand
    return p


def lint_skill(skill_md: Path, repo_root: Path | None = None) -> Report:
    skill_md = Path(skill_md)
    try:
        rel = str(skill_md.resolve().relative_to(Path.cwd()))
    except ValueError:
        rel = str(skill_md)
    rep = Report(path=rel)
    add = lambda rule, level, msg, line=None: rep.findings.append(Finding(rule, level, msg, rel, line))

    if not skill_md.is_file():
        add("DSK001", ERROR, "SKILL.md not found")
        return rep
    try:
        text = skill_md.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        add("DSK001", ERROR, "SKILL.md is not valid UTF-8")
        return rep

    block, body = fm.split(text)
    if block is None:
        add("DSK001", ERROR, "no YAML frontmatter block (`---` … `---`) at top of file", 1)
        return rep
    try:
        meta = fm.parse(block)
    except fm.ParseError as e:
        add("DSK010", ERROR, f"frontmatter is not valid YAML: {e}", 1)
        return rep

    skill_dir = skill_md.parent
    root = Path(repo_root) if repo_root else _repo_root(skill_dir)

    # --- keys
    unknown = sorted(k for k in meta if k not in KNOWN_KEYS)
    if unknown:
        add("DSK010", WARN, f"unrecognised frontmatter key(s): {', '.join(unknown)} (put custom fields under `metadata:`)", 1)

    # --- name
    name = meta.get("name")
    if not isinstance(name, str) or not name.strip():
        add("DSK011", ERROR, "`name` is required", 1)
    else:
        rep.name = name
        if not (1 <= len(name) <= 64) or not NAME_RE.match(name):
            add("DSK011", ERROR, f"`name` must be 1–64 chars of lowercase letters, digits and hyphens: got {name!r}", 1)
        if name.lower() in GENERIC_NAMES:
            add("DSK015", WARN, f"`name` {name!r} is generic — pick something specific", 1)
        if skill_dir.resolve() != root.resolve() and skill_dir.name != name:
            add("DSK002", WARN, f"directory {skill_dir.name!r} does not match `name` {name!r}", 1)

    # --- description
    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        add("DSK012", ERROR, "`description` is required", 1)
    else:
        d = re.sub(r"\s+", " ", desc).strip()
        if len(d) < 20:
            add("DSK012", ERROR, f"`description` is too short ({len(d)} chars, minimum 20)", 1)
        elif len(d) > 1024:
            add("DSK012", ERROR, f"`description` is too long ({len(d)} chars, maximum 1024)", 1)
        if not TRIGGER_RE.search(d):
            add("DSK013", WARN, "`description` should say when to use the skill (e.g. \"Use when the user …\")", 1)
        if HYPE_RE.search(d):
            add("DSK014", WARN, "`description` reads like marketing — write it for the agent (no `!`, no \"best\"/\"ultimate\")", 1)

    # --- optional fields
    if "allowed-tools" in meta:
        at = meta["allowed-tools"]
        if not at or (isinstance(at, str) and not at.strip()):
            add("DSK018", ERROR, "`allowed-tools` is present but empty", 1)
    md = meta.get("metadata")
    ver = None
    if isinstance(md, dict):
        ver = md.get("version")
    ver = ver or meta.get("version")
    if ver is not None and not SEMVER_RE.match(str(ver)):
        add("DSK017", WARN, f"`version` {ver!r} is not a semantic version (e.g. 1.2.0)", 1)
    if ver is None:
        add("DSK017", INFO, "no `metadata.version` — versioning helps users track changes", 1)
    if "license" in meta and not isinstance(meta["license"], str):
        add("DSK016", WARN, "`license` should be an SPDX identifier string", 1)

    # --- body
    body_stripped = body.strip()
    body_lines = body_stripped.count("\n") + 1 if body_stripped else 0
    if len(body_stripped) < 200:
        add("DSK020", ERROR, f"body has {len(body_stripped)} chars of instructions (minimum 200)")
    else:
        if not re.search(r"^#{1,6}\s+\S", body_stripped, re.M):
            add("DSK021", WARN, "body has no headings — structure the instructions with `##` sections")
        if body_lines > 500:
            add("DSK022", WARN, f"body is {body_lines} lines (recommended ≤ 500) — move reference material to references/")
        if isinstance(desc, str) and body_stripped.replace("#", "").strip() == desc.strip():
            add("DSK023", WARN, "body only repeats the description — add actual instructions")

    # --- referenced files
    missing = []
    for ref in sorted(set(REF_RE.findall(body))):
        ref = ref.rstrip(".,;:)")
        if ref.endswith("/") or "*" in ref or "{" in ref or "<" in ref:
            continue
        if not (skill_dir / ref).exists() and not (root / ref).exists():
            missing.append(ref)
    if missing:
        add("DSK003", WARN, f"referenced file(s) not found: {', '.join(missing[:6])}{' …' if len(missing) > 6 else ''}")

    # --- safety (frontmatter + body)
    for rx, what in SECRET_RES:
        if rx.search(text):
            add("DSK030", ERROR, f"possible embedded secret: {what}", _line_of(text, rx))
    for rx, what in DANGER_RES:
        if rx.search(text):
            add("DSK031", WARN, f"dangerous shell pattern: {what}", _line_of(text, rx))
    if EVASION_RE.search(text):
        add("DSK033", WARN, "instruction appears to hide actions from, or bypass confirmation by, the user", _line_of(text, EVASION_RE))
    if re.search(r"(https?:\s*['\"]\s*\+|['\"]\s*\+\s*['\"]\s*(//|\.com|\.ai|\.io))", text):
        add("DSK032", WARN, "URL appears to be assembled from string fragments — write network destinations in plain text")

    # --- repo
    has_license_file = any((root / n).exists() for n in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"))
    if not has_license_file and "license" not in meta:
        add("DSK040", WARN, "no LICENSE file in repository and no `license` in frontmatter")
    if not any((root / n).exists() for n in ("README.md", "README", "readme.md", "README.zh.md")):
        add("DSK041", WARN, "no README.md in repository root")

    rep.findings.sort(key=lambda f: ({ERROR: 0, WARN: 1, INFO: 2}[f.level], f.rule))
    return rep


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}


def discover(paths: list[str | Path]) -> list[Path]:
    """Expand files/directories to SKILL.md paths."""
    found: list[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_file():
            found.append(p)
        elif p.is_dir():
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                if "SKILL.md" in filenames:
                    found.append(Path(dirpath) / "SKILL.md")
    return sorted(set(found))


def lint_path(path: str | Path) -> list[Report]:
    return [lint_skill(f) for f in discover([path])]
