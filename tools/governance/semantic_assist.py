#!/usr/bin/env python3

import pathlib, re, sys, json, yaml

COMMENT = {
    ".py": "#",
    ".js": "//",
    ".jsx": "//",
    ".ts": "//",
    ".tsx": "//",
    ".dart": "//",
    ".kt": "//",
    ".java": "//",
    ".go": "//",
    ".rb": "#",
    ".sh": "#",
    ".yaml": "#",
    ".yml": "#",
    ".md": "<!-- -->",
}


def tag_line(suf, tag):
    return (
        (COMMENT.get(suf, "//") + " @Study:" + tag)
        if suf != ".md"
        else f"<!-- @Study:{tag} -->"
    )


def apply_tag(path: pathlib.Path, st: str, apply=False):
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except:
        return False
    head = "\n".join(txt.splitlines()[:25])
    if f"@Study:{st}" in head:
        return False
    line = tag_line(path.suffix.lower(), st)
    if apply:
        path.write_text(line + "\n" + txt, encoding="utf-8")
    return True


root = pathlib.Path(".")
rules = yaml.safe_load(pathlib.Path("governance/studies/boost_rules.yaml").read_text())[
    "rules"
]
apply = "--apply" in sys.argv
limit = 200

for st, cfg in rules.items():
    kws = [re.compile(re.escape(k), re.I) for k in cfg.get("keywords", [])]
    matches = []
    for p in root.rglob("*"):
        if not p.is_file() or ".git" in p.as_posix():
            continue
        if p.suffix.lower() not in COMMENT:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except:
            continue
        if any(k.search(txt) for k in kws):
            matches.append(p)
            if len(matches) >= limit:
                break
    touched = 0
    for m in matches:
        changed = apply_tag(m, st, apply=apply)
        if changed:
            touched += 1
    print(
        f"{'APPLY' if apply else 'DRY'} | {st} | candidates={len(matches)} | tagged={touched}"
    )

if not apply:
    print("Run with --apply to write changes.")
