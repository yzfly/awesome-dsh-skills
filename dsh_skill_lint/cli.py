"""Command-line entry point: `dsh-skill-lint [paths...]`."""

from __future__ import annotations

import argparse
import json
import sys

from . import SPEC_VERSION, __version__
from .linter import ERROR, INFO, WARN, discover, lint_skill

C = {
    "reset": "\033[0m", "dim": "\033[2m", "bold": "\033[1m",
    ERROR: "\033[31m", WARN: "\033[33m", INFO: "\033[36m",
    "A": "\033[32m", "B": "\033[36m", "C": "\033[33m", "D": "\033[31m",
}


def paint(s: str, *keys: str, on: bool) -> str:
    return "".join(C[k] for k in keys) + s + C["reset"] if on else s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="dsh-skill-lint",
        description=f"Check SKILL.md files against the DSH Skill Specification {SPEC_VERSION}.",
    )
    ap.add_argument("paths", nargs="*", default=["."], help="SKILL.md files or directories to scan (default: .)")
    ap.add_argument("--format", choices=["text", "json", "github"], default="text")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    ap.add_argument("--min-score", type=int, default=None, help="exit non-zero if any skill scores below this")
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--version", action="version", version=f"dsh-skill-lint {__version__} (spec {SPEC_VERSION})")
    a = ap.parse_args(argv)

    files = discover(a.paths)
    if not files:
        print("no SKILL.md found under: " + ", ".join(a.paths), file=sys.stderr)
        return 2
    reports = [lint_skill(f) for f in files]
    color = a.format == "text" and not a.no_color and sys.stdout.isatty()

    if a.format == "json":
        print(json.dumps({"spec": SPEC_VERSION, "version": __version__, "skills": [r.as_dict() for r in reports]}, ensure_ascii=False, indent=2))
    elif a.format == "github":
        for r in reports:
            for f in r.findings:
                lvl = {ERROR: "error", WARN: "warning", INFO: "notice"}[f.level]
                loc = f"file={f.path}" + (f",line={f.line}" if f.line else "")
                print(f"::{lvl} {loc},title={f.rule}::{f.message}")
    else:
        for r in reports:
            head = f"{paint(r.grade, r.grade, 'bold', on=color)} {r.score:>3}  {paint(r.path, 'bold', on=color)}"
            if r.name:
                head += paint(f"  ({r.name})", "dim", on=color)
            print(head)
            for f in r.findings:
                tag = {ERROR: "✖", WARN: "▲", INFO: "·"}[f.level]
                where = paint(f":{f.line}", "dim", on=color) if f.line else ""
                print(f"   {paint(tag + ' ' + f.rule, f.level, on=color)}{where}  {f.message}")
            if not r.findings:
                print(paint("   ✓ conformant, no findings", "A", on=color))
        n = len(reports)
        ok = sum(1 for r in reports if r.conformant)
        avg = sum(r.score for r in reports) / n
        print()
        print(paint(f"{n} skill{'s' if n != 1 else ''} · {ok} conformant · average score {avg:.0f} · spec {SPEC_VERSION}", "dim", on=color))

    failed = any(not r.conformant for r in reports)
    if a.strict:
        failed = failed or any(r.warnings for r in reports)
    if a.min_score is not None:
        failed = failed or any(r.score < a.min_score for r in reports)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
