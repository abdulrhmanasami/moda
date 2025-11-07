#!/usr/bin/env python3

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"; OUT.mkdir(parents=True, exist_ok=True)

CFG   = ROOT / "governance" / "drift_guard.config.json"
R_CUR = ROOT / "reports" / "REALITY_TEST.json"
D_CUR = ROOT / "reports" / "DOCMAP_SYNC.json"
C_CUR = ROOT / "reports" / "CLEAN_RELEASE_REPORT.json"

R_BASE = ROOT / "governance" / "baselines" / "REALITY_BASELINE.json"
D_BASE = ROOT / "governance" / "baselines" / "DOCMAP_BASELINE.json"
C_BASE = ROOT / "governance" / "baselines" / "CLEAN_BASELINE.json"

def J(p):
  return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def get(d, path, default=None):
  cur = d
  for part in path.split("."):
    if isinstance(cur, dict) and part in cur: cur = cur[part]
    else: return default
  return cur

def main():
  cfg = J(CFG)
  curR, curD, curC = J(R_CUR), J(D_CUR), J(C_CUR)
  baseR, baseD, baseC = J(R_BASE), J(D_BASE), J(C_BASE)

  issues_hard, issues_soft = [], []

  # 1) Endpoints / Tests minimums
  cur_endp  = get(curR, "snapshot.endpoints_count", 0)
  cur_tests  = get(curR, "snapshot.tests_count", 0)

  if cur_endp < cfg["hard_fail"]["endpoints_min"]:
    issues_hard.append(f"Endpoints below minimum: {cur_endp} < {cfg['hard_fail']['endpoints_min']}")
  if cur_tests < cfg["hard_fail"]["tests_min"]:
    issues_hard.append(f"Tests below minimum: {cur_tests} < {cfg['hard_fail']['tests_min']}")

  # 2) DocMap (missing/orphan)
  cur_missing = len(get(curD, "missing", []) or [])
  orphan_list = get(curD, "orphan", []) or []
  # Exclude the index file itself from orphan count
  filtered_orphans = [o for o in orphan_list if not o.endswith("MASTER_STUDIES_INDEX.md")]
  cur_orphan  = len(filtered_orphans)
  if cur_missing > cfg["hard_fail"]["doc_missing"]:
    issues_hard.append(f"Doc missing > 0: {cur_missing}")
  if cur_orphan > cfg["hard_fail"]["doc_orphan"]:
    issues_hard.append(f"Doc orphan > 0: {cur_orphan}")

  # 3) Clean Release checks removed - handled by preflight/claims

  # 4) Repo size drift (approx from CLEAN report summary if موجود)
  size_mb_cur  = float(get(curC, "summary.total_megabytes", 0.0) or 0.0)
  size_mb_base = float(get(baseC, "summary.total_megabytes", 0.0) or 0.0)
  if (size_mb_cur - size_mb_base) > float(cfg["soft_fail"]["repo_size_grow_mb"]):
    issues_soft.append(f"Repo size +{round(size_mb_cur - size_mb_base,3)} MB > allowed {cfg['soft_fail']['repo_size_grow_mb']}")

  # 5) Unknown languages/creep
  if cfg["hard_fail"]["unknown_langs"]:
    cur_langs  = get(curR, "snapshot.langs_files", {}) or {}
    base_langs = get(baseR, "snapshot.langs_files", {}) or {}
    unknown = [lang for lang in cur_langs.keys() if lang not in base_langs.keys()]
    if unknown:
      issues_hard.append(f"Unknown languages appeared: {unknown}")

  # تقارير
  report = {
    "current": {
      "endpoints": cur_endp, "tests": cur_tests,
      "doc_missing": cur_missing, "doc_orphan": cur_orphan,
      "repo_size_mb": size_mb_cur
    },
    "issues_hard": issues_hard,
    "issues_soft": issues_soft
  }
  (OUT / "DRIFT_GUARD.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

  md = [
    "# Drift Guard Report",
    f"- Endpoints: {cur_endp} (min required: {cfg['hard_fail']['endpoints_min']})",
    f"- Tests: {cur_tests} (min required: {cfg['hard_fail']['tests_min']})",
    f"- Doc missing: {cur_missing} (max allowed: {cfg['hard_fail']['doc_missing']})",
    f"- Doc orphan: {cur_orphan} (max allowed: {cfg['hard_fail']['doc_orphan']})",
    f"- Repo Size (MB): {size_mb_cur}",
    f"- Unknown languages check: {'enabled' if cfg['hard_fail']['unknown_langs'] else 'disabled'}",
    "## Hard Issues" if issues_hard else "## Hard Issues\n- None",
  ]
  if issues_hard:
    md += [f"- {x}" for x in issues_hard]
  md += ["\n## Soft Issues" if issues_soft else "\n## Soft Issues\n- None"]
  if issues_soft:
    md += [f"- {x}" for x in issues_soft]
  (OUT / "DRIFT_GUARD.md").write_text("\n".join(md), encoding="utf-8")

  if issues_hard:
    print("❌ Drift Guard: hard drift detected. See reports/DRIFT_GUARD.*")
    sys.exit(1)
  if issues_soft:
    print("⚠️ Drift Guard: soft drift detected. See reports/DRIFT_GUARD.*")
  print("✅ Drift Guard passed.")
  return 0

if __name__ == "__main__":
  sys.exit(main())
