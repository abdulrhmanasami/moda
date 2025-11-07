#!/usr/bin/env python3

import re, json, sys

from pathlib import Path



ROOT = Path(__file__).resolve().parents[2]

INDEX = ROOT / "studies" / "MASTER_STUDIES_INDEX.md"

OUT   = ROOT / "reports"

OUT.mkdir(parents=True, exist_ok=True)



def extract_paths(md:str):
    # يلتقط مسارات داخل أقواس ماركداون: [نص](path/to/file.ext)
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", md)

    # يلتقط مسارات في كود بلوكس أو inline code
    code_links = re.findall(r"`(studies\/[^`\s]+)`", md)  # Only in backticks

    # يلتقط مسارات محددة للمجلدات الفرعية مع أسماء الملفات
    subfolder_patterns = [
        r'core_strategy/([a-zA-Z0-9_\u0600-\u06FF\-]+\.md)',
        r'technical_specs/([a-zA-Z0-9_\u0600-\u06FF\-]+\.md)',
        r'business_analysis/([a-zA-Z0-9_\u0600-\u06FF\-]+\.md)',
        r'implementation_phases/([a-zA-Z0-9_\u0600-\u06FF\-]+\.md)',
        r'compliance_governance/([a-zA-Z0-9_\u0600-\u06FF\-]+\.md)',
        r'master_studies/([a-zA-Z0-9_\u0600-\u06FF\-]+\.md)'
    ]

    subfolder_links = []
    for pattern in subfolder_patterns:
        matches = re.findall(pattern, md)
        for match in matches:
            # نحصل على اسم المجلد من النمط
            folder = pattern.split('/')[0]
            subfolder_links.append(f'studies/{folder}/{match}')

    # نجمع جميع الروابط ونفلتر الغير صحيحة
    all_links = set([*links, *code_links, *subfolder_links])

    # نستثني الروابط غير الصحيحة مثل studies/** أو studies/*
    filtered_links = [link for link in all_links if not link.endswith('/**') and not link.endswith('/*') and link.startswith('studies/')]

    return sorted(filtered_links)



def main():
    missing, referenced, present, orphan = [], [], [], []

    if not INDEX.exists():
        print("⚠️ MASTER_STUDIES_INDEX.md مفقود")
        print("[]"); sys.exit(1)

    md = INDEX.read_text(encoding="utf-8")
    refs = [p for p in extract_paths(md) if p.startswith("studies/")]
    referenced = []

    for p in refs:
        try:
            path = (ROOT / p).resolve()
            referenced.append(p)
        except Exception:
            continue

    # موجود فعلياً تحت studies/
    actual = [str(p.relative_to(ROOT)) for p in (ROOT/"studies").rglob("*") if p.is_file() and p.name != "MASTER_STUDIES_INDEX.md"]

    ref_set, act_set = set(referenced), set(actual)
    missing = sorted(list(ref_set - act_set))
    orphan  = sorted(list(act_set - ref_set))

    # تقارير
    report = {
        "referenced_count": len(referenced),
        "actual_count": len(actual),
        "missing": missing,
        "orphan": orphan
    }

    (OUT / "DOCMAP_SYNC.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if missing or orphan:
        print("❌ DocMap out of sync:")
        if missing:
            print(f"  Missing: {len(missing)} files")
            for m in missing:
                print(f"    - {m}")
        if orphan:
            print(f"  Orphan: {len(orphan)} files")
            for o in orphan:
                print(f"    - {o}")
        sys.exit(1)
    else:
        print("✅ DocMap in sync.")

if __name__ == "__main__":
    main()
