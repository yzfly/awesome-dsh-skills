"""Minimal YAML-subset parser for SKILL.md frontmatter (no dependencies).

Supports what skills actually use: `key: value`, quoted strings, `>` / `|`
block scalars, one level of nested mapping (`metadata:`), `- item` lists,
booleans and comments. Anything stranger raises ParseError, which the linter
reports as DSK010.
"""

from __future__ import annotations

import re

FM_RE = re.compile(r"\A﻿?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


class ParseError(ValueError):
    pass


def split(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_block, body). Block is None when absent."""
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def _scalar(raw: str):
    s = raw.strip()
    if s == "" or s == "~" or s == "null":
        return None
    if (s[0] == s[-1]) and s[0] in "\"'" and len(s) >= 2:
        return s[1:-1]
    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    # strip trailing comment
    s = re.sub(r"\s+#.*$", "", s)
    return s


def parse(block: str) -> dict:
    lines = block.replace("\r\n", "\n").split("\n")
    out: dict = {}
    i = 0
    n = len(lines)

    def indent(s: str) -> int:
        return len(s) - len(s.lstrip(" "))

    while i < n:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if "\t" in line[: indent(line) + 1]:
            raise ParseError(f"line {i+1}: tabs are not allowed for indentation")
        if indent(line) != 0:
            raise ParseError(f"line {i+1}: unexpected indentation")
        m = re.match(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$", line)
        if not m:
            raise ParseError(f"line {i+1}: expected `key: value`")
        key, rest = m.group(1), m.group(2)
        i += 1
        if rest in (">", "|", ">-", "|-", ">+", "|+"):
            buf = []
            while i < n and (lines[i].strip() == "" or indent(lines[i]) > 0):
                buf.append(lines[i].strip() if rest[0] == ">" else lines[i].lstrip(" "))
                i += 1
            joined = " ".join(b for b in buf if b) if rest[0] == ">" else "\n".join(buf)
            out[key] = joined.strip()
        elif rest == "" or rest.startswith("#"):
            # nested mapping or list
            child: dict = {}
            items: list = []
            while i < n and (lines[i].strip() == "" or indent(lines[i]) > 0):
                l = lines[i]
                if not l.strip():
                    i += 1
                    continue
                s = l.strip()
                if s.startswith("- "):
                    items.append(_scalar(s[2:]))
                else:
                    mm = re.match(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$", s)
                    if not mm:
                        raise ParseError(f"line {i+1}: expected nested `key: value`")
                    child[mm.group(1)] = _scalar(mm.group(2))
                i += 1
            out[key] = items if items and not child else child
        elif rest.startswith("[") and rest.endswith("]"):
            out[key] = [_scalar(x) for x in rest[1:-1].split(",") if x.strip()]
        else:
            out[key] = _scalar(rest)
    return out
