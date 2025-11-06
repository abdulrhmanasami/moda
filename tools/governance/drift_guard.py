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

  # 1) Endpoints / Tests
  cur_endp  = get(curR, "snapshot.endpoints_count", 0)
  base_endp = get(baseR, "snapshot.endpoints_count", 0)
  cur_tests  = get(curR, "snapshot.tests_count", 0)
  base_tests = get(baseR, "snapshot.tests_count", 0)

  if cur_endp - base_endp < cfg["hard_fail"]["endpoints_min_delta"]:
    issues_hard.append(f"Endpoints dropped: {cur_endp} < {base_endp}")
  if cur_tests - base_tests < cfg["hard_fail"]["tests_min_delta"]:
    issues_hard.append(f"Tests dropped: {cur_tests} < {base_tests}")

  # 2) DocMap (missing/orphan)
  cur_missing = len(get(curD, "missing", []) or [])
  cur_orphan  = len(get(curD, "orphan", []) or [])
  if cur_missing > cfg["hard_fail"]["doc_missing_max"]:
    issues_hard.append(f"Doc missing > 0: {cur_missing}")
  if cur_orphan > cfg["hard_fail"]["doc_orphan_max"]:
    issues_hard.append(f"Doc orphan > 0: {cur_orphan}")

  # 3) Clean Release (root + forbidden + archives + oversized)
  illegal_files = len(get(curC, "root.illegal_files", []) or [])
  illegal_dirs  = len(get(curC, "root.illegal_dirs", []) or [])
  forbidden     = len(get(curC, "forbidden_matches", []) or [])
  archives_out  = len(get(curC, "archives_outside_dist", []) or [])
  oversized     = len(get(curC, "oversized", []) or [])

  if illegal_files > cfg["hard_fail"]["root_illegal_files_max"]:
    issues_hard.append(f"Illegal root files: {illegal_files}")
  if illegal_dirs > cfg["hard_fail"]["root_illegal_dirs_max"]:
    issues_hard.append(f"Illegal root dirs: {illegal_dirs}")
  if forbidden > cfg["hard_fail"]["forbidden_matches_max"]:
    issues_hard.append(f"Forbidden matches: {forbidden}")
  if archives_out > cfg["hard_fail"]["archives_outside_dist_max"]:
    issues_hard.append(f"Archives outside dist: {archives_out}")
  if oversized > cfg["soft_fail"]["oversized_files_max"]:
    issues_soft.append(f"Oversized files: {oversized}")

  # 4) Repo size drift (approx from CLEAN report summary if موجود)
  size_mb_cur  = float(get(curC, "summary.total_megabytes", 0.0) or 0.0)
  size_mb_base = float(get(baseC, "summary.total_megabytes", 0.0) or 0.0)
  if (size_mb_cur - size_mb_base) > float(cfg["soft_fail"]["repo_size_mb_increase_max"]):
    issues_soft.append(f"Repo size +{round(size_mb_cur - size_mb_base,3)} MB > allowed {cfg['soft_fail']['repo_size_mb_increase_max']}")

  # 5) Unknown languages/creep
  cur_langs  = get(curR, "snapshot.langs_files", {}) or {}
  base_langs = get(baseR, "snapshot.langs_files", {}) or {}
  unknown = [lang for lang in cur_langs.keys() if lang not in base_langs.keys()]
  if cfg.get("fail_on_unknown_language", True) and unknown:
    issues_hard.append(f"Unknown languages appeared: {unknown}")

  # تقارير
  report = {
    "baseline": {
      "endpoints": base_endp, "tests": base_tests,
      "repo_size_mb": size_mb_base, "langs": base_langs
    },
    "current": {
      "endpoints": cur_endp, "tests": cur_tests,
      "repo_size_mb": size_mb_cur, "langs": cur_langs
    },
    "deltas": {
      "endpoints": cur_endp - base_endp,
      "tests": cur_tests - base_tests,
      "repo_size_mb": round(size_mb_cur - size_mb_base, 3)
    },
    "issues_hard": issues_hard,
    "issues_soft": issues_soft
  }
  (OUT / "DRIFT_GUARD.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

  md = [
    "# Drift Guard Report",
    f"- Endpoints: {cur_endp} (Δ {cur_endp - base_endp}) vs baseline {base_endp}",
    f"- Tests: {cur_tests} (Δ {cur_tests - base_tests}) vs baseline {base_tests}",
    f"- Repo Size (MB): {size_mb_cur} (Δ {round(size_mb_cur - size_mb_base,3)}) vs {size_mb_base}",
    f"- Unknown languages: {', '.join(unknown) if unknown else '—'}",
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
