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

  # يلتقط كمان كود بلوكس فيها مسارات studies/*

  code_links = re.findall(r"(studies\/[^\s)]+)", md)

  # يلتقط مسارات محددة للمجلدات الفرعية مع أسماء الملفات
  # مثل: core_strategy/00_الملخص_التنفيذي_الشامل_المحسن.md

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

  actual = [str(p.relative_to(ROOT)) for p in (ROOT/"studies").rglob("*") if p.is_file()]



  ref_set, act_set = set(referenced), set(actual)

  missing = sorted(list(ref_set - act_set))

  orphan  = sorted(list(act_set - ref_set))



  data = {

    "referenced_count": len(ref_set),

    "actual_count": len(act_set),

    "missing": missing,

    "orphan": orphan

  }

  (OUT/"DOCMAP_SYNC.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")



  (OUT/"DOCMAP_SYNC.md").write_text(

    "# Doc Map Sync\n\n"

    f"- Referenced in index: **{len(ref_set)}**\n"

    f"- Actual files under studies/: **{len(act_set)}**\n"

    f"- Missing: **{len(missing)}**\n"

    f"- Orphan: **{len(orphan)}**\n\n"

    "## Missing\n" + "\n".join(f"- {m}" for m in missing) + "\n\n"

    "## Orphan\n"  + "\n".join(f"- {o}" for o in orphan) + "\n",

    encoding="utf-8"

  )



  # فشل إذا في فرق

  cfg_path = ROOT / "governance" / "preflight.config.json"

  fail_on_missing = True

  fail_on_orphans = True

  if cfg_path.exists():

    import json as _j

    c = _j.loads(cfg_path.read_text(encoding="utf-8"))

    fail_on_missing = c.get("fail_on_missing", True)

    fail_on_orphans = c.get("fail_on_orphans", True)



  if (fail_on_missing and missing) or (fail_on_orphans and orphan):

    print("❌ DocMap out-of-sync. راجع reports/DOCMAP_SYNC.*")

    sys.exit(1)



  print("✅ DocMap in sync.")

  return 0



if __name__ == "__main__":

  sys.exit(main())
