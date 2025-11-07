#!/usr/bin/env python3

import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)

def check_root_cleanliness():
    """فحص نظافة الجذر"""
    config_path = ROOT / "governance" / "preflight.config.json"
    if not config_path.exists():
        return {"error": "preflight.config.json not found"}

    config = json.loads(config_path.read_text())

    root_files = [f for f in os.listdir(ROOT) if os.path.isfile(f)]
    root_dirs = [d for d in os.listdir(ROOT) if os.path.isdir(d)]

    forbidden_files = config.get("forbidden_root", [])
    allowed_files = config.get("allowed_root", [])

    illegal_files = []
    illegal_dirs = []

    for file in root_files:
        if file not in allowed_files and any(file.endswith(f[1:]) if f.startswith("*") else file == f for f in forbidden_files):
            illegal_files.append(file)

    for dir in root_dirs:
        # تجاهل مجلدات النظام
        if dir.startswith('.') and dir != '.github':
            continue
        if f"{dir}/" not in allowed_files:
            illegal_dirs.append(dir)

    return {
        "root.illegal_files": illegal_files,
        "root.illegal_dirs": illegal_dirs,
        "summary": {
            "total_files": len(root_files),
            "total_dirs": len(root_dirs),
            "illegal_files_count": len(illegal_files),
            "illegal_dirs_count": len(illegal_dirs)
        }
    }

def main():
    results = check_root_cleanliness()

    # كتابة التقرير
    (OUT / "CLEAN_RELEASE_REPORT.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # فحص الفشل
    if results.get("root.illegal_files") or results.get("root.illegal_dirs"):
        print("❌ Clean Release FAILED:")
        if results["root.illegal_files"]:
            print(f"  Illegal files: {results['root.illegal_files']}")
        if results["root.illegal_dirs"]:
            print(f"  Illegal dirs: {results['root.illegal_dirs']}")
        sys.exit(1)
    else:
        print("✅ Clean Release PASSED")

if __name__ == "__main__":
    main()
