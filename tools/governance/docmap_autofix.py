#!/usr/bin/env python3

import re, json

from pathlib import Path



ROOT=Path(__file__).resolve().parents[2]

idx=ROOT/"studies"/"MASTER_STUDIES_INDEX.md"

all_files=sorted([p for p in (ROOT/"studies").rglob("*.md") if "MASTER_STUDIES_INDEX.md" not in p.name])

lines=[f"- [{p.stem}]({p.relative_to(ROOT).as_posix()})" for p in all_files]

out=["# MASTER STUDIES INDEX (Auto-Fixed)\n","",*lines, ""]

idx.write_text("\n".join(out), encoding="utf-8")

print("[OK] MASTER_STUDIES_INDEX.md regenerated with", len(all_files), "entries.")
