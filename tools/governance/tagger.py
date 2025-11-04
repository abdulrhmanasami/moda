# @Study:ST-019
#!/usr/bin/env python3

import sys, re, json, yaml, pathlib, fnmatch

COMMENT = {
  ".py": "#", ".js": "//", ".jsx": "//", ".ts": "//", ".tsx": "//",
  ".dart": "//", ".kt": "//", ".java": "//", ".go": "//", ".rb": "#",
  ".sh": "#", ".yaml": "#", ".yml": "#", ".md": "#", ".json": "//",
  ".toml": "#", ".lock": "#", ".txt": "#"
}

def comment_line(suffix, text):
    c = COMMENT.get(suffix, "//")
    return f"{c} {text}"

def ensure_tag(path, studies, apply=False):
    suf = path.suffix.lower()
    tag = " ".join([f"@Study:{s}" for s in studies])
    header = comment_line(suf, tag)
    
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False, "skip(read)"
    
    lines = txt.splitlines()
    head = "\n".join(lines[:25])
    
    if re.search(r"@Study:ST-\d{3}", head):
        # حدّث الوسوم لو ناقصة
        existing_studies = set(re.findall(r"@Study:(ST-\d{3})", head))
        new_studies = set(studies)
        if existing_studies >= new_studies:
            return False, "ok(already)"
        
        # أضف الوسوم الناقصة
        missing = new_studies - existing_studies
        if missing:
            # أضف في نهاية السطر الأول الذي يحتوي على @Study
            new_head = re.sub(
                r"(@Study:.*)$",
                lambda m: m.group(1) + " " + " ".join([f"@Study:{s}" for s in sorted(missing)]),
                head,
                count=1,
                flags=re.M
            )
            new_txt = new_head + "\n" + "\n".join(lines[25:])
            if apply:
                path.write_text(new_txt, encoding="utf-8")
            return True, "update"
    else:
        new_txt = header + "\n" + txt
        if apply:
            path.write_text(new_txt, encoding="utf-8")
        return True, "insert"
    
    return False, "ok(already)"

def load_map():
    cfg = yaml.safe_load(pathlib.Path("governance/studies/tagging_map.yaml").read_text())
    return cfg.get("patterns", [])

def match_files(glob):
    root = pathlib.Path(".")
    for p in root.rglob("*"):
        if p.is_file() and not any(seg.startswith(".git") for seg in p.parts):
            try:
                if fnmatch.fnmatch(str(p).replace("\\","/"), glob):
                    yield p
            except Exception:
                continue

def main():
    apply = "--apply" in sys.argv
    patterns = load_map()
    touched = 0
    
    for rule in patterns:
        glb = rule["glob"]; studies = rule["studies"]
        for f in match_files(glb):
            if f.suffix.lower() not in COMMENT: 
                continue
            changed, status = ensure_tag(f, studies, apply=apply)
            if changed: touched += 1
            print(f"{'APPLY' if apply else 'DRY'} | {status:8} | {f}")
    
    print(f"==> Files {'modified' if apply else 'would change'}: {touched}")
    if not apply:
        print("Run with --apply to write changes.")

if __name__ == "__main__":
    main()
