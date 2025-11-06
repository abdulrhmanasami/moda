#!/usr/bin/env python3

import os, re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG  = ROOT / "governance" / "reality_test.config.json"
OUTD = ROOT / "reports"; OUTD.mkdir(parents=True, exist_ok=True)

def load_cfg():
  if CFG.exists():
    return json.loads(CFG.read_text(encoding="utf-8"))
  return {
    "expect_frontend": True, "expect_backend": True, "expect_db": True,
    "expect_tests": True, "expect_ci_gates": [], "fail_on": [], "soft_fail_on":[]
  }

def files(glob): return list(ROOT.rglob(glob))

def has_frontend():
  pkg = ROOT / "src" / "frontend" / "package.json"
  if pkg.exists():
    try:
      import json as _j
      data = _j.loads(pkg.read_text(encoding="utf-8"))
      return "next" in (data.get("dependencies") or {}) or "next" in (data.get("devDependencies") or {})
    except Exception: pass
  # وجود أي من ملفات Next.js
  return any((ROOT / "src" / "frontend" / f).exists() for f in ["next.config.js","next.config.ts","app","pages"])

def has_backend():
  # وجود FastAPI أو أي نقطة نهاية مع @app.<method>
  py_files = [p for p in files("*.py") if "htmlcov" not in str(p)]
  for p in py_files:
    try:
      t = p.read_text(encoding="utf-8", errors="ignore")
      if "fastapi" in t or re.search(r"@app\.(get|post|put|delete|patch)\(", t):
        return True
    except: pass
  return False

def has_db():
  # Alembic / migrations / docker-compose مع postgres / helm chart للـ DB
  if (ROOT/"alembic.ini").exists(): return True
  if list((ROOT/"migrations").glob("**/*")): return True
  if any("postgres" in p.read_text(encoding="utf-8", errors="ignore").lower()
         for p in files("**/docker-compose*.y*ml")): return True
  if list((ROOT/"infrastructure").glob("**/*.tf")): return True
  if list((ROOT/"infrastructure" / "helm").glob("**/*")): return True
  return False

def tests_stats():
  count = 0
  for pat in ["tests/**/*.py","**/*.spec.ts","**/*.spec.tsx","**/*.test.ts","**/*.test.tsx"]:
    count += len(files(pat))
  return count

def ci_gates_present():
  names = set()
  for w in (ROOT/".github"/"workflows").glob("*.yml"):
    try:
      txt = w.read_text(encoding="utf-8", errors="ignore")
      if "gitleaks" in txt.lower(): names.add("gitleaks")
      if "codeql"  in txt.lower():
        names.add("CodeQL / Analyze (javascript-typescript)")
        names.add("CodeQL / Analyze (python)")
    except: pass
  return names

def endpoints_count():
  c = 0
  for p in files("**/*.py"):
    try:
      t = p.read_text(encoding="utf-8", errors="ignore")
      c += len(re.findall(r"@app\.(get|post|put|delete|patch)\(", t))
    except: pass
  return c

def reality_snapshot():
  langs = {"py":len(files("**/*.py")),
           "ts":len(files("**/*.ts"))+len(files("**/*.tsx")),
           "js":len(files("**/*.js"))+len(files("**/*.jsx")),
           "dart":len(files("**/*.dart"))}
  return {
    "langs_files": langs,
    "frontend": has_frontend(),
    "backend": has_backend(),
    "db": has_db(),
    "tests_count": tests_stats(),
    "endpoints_count": endpoints_count(),
    "ci_gates_found": sorted(list(ci_gates_present()))
  }

def assess(snap, cfg):
  issues = []
  if cfg.get("expect_frontend") and not snap["frontend"]:
    issues.append(("missing_frontend","Frontend not detected (Next.js)."))
  if cfg.get("expect_backend") and not snap["backend"]:
    issues.append(("missing_backend","Backend (FastAPI/endpoints) not detected."))
  if cfg.get("expect_db") and not snap["db"]:
    issues.append(("missing_db","Database layer not detected (alembic/migrations/postgres infra)."))
  if cfg.get("expect_tests") and snap["tests_count"] < 5:
    issues.append(("low_tests",f"Low tests count: {snap['tests_count']} (<5)."))
  # تحقق من بوابات CI
  expected = set(cfg.get("expect_ci_gates",[]))
  missing = [g for g in expected if g not in set(snap["ci_gates_found"])]
  if missing:
    issues.append(("missing_ci_gates", f"Missing CI gates: {missing}"))
  return issues

def write_reports(snap, issues):
  OUTD.joinpath("REALITY_TEST.json").write_text(json.dumps({"snapshot":snap,"issues":issues}, ensure_ascii=False, indent=2), encoding="utf-8")

  md = ["# Governance Reality Test",
        "## Snapshot",
        f"- Languages (files): {snap['langs_files']}",
        f"- Frontend (Next.js): {'✅' if snap['frontend'] else '❌'}",
        f"- Backend (FastAPI/endpoints): {'✅' if snap['backend'] else '❌'} (endpoints: {snap['endpoints_count']})",
        f"- Database layer: {'✅' if snap['db'] else '❌'}",
        f"- Tests count: {snap['tests_count']}",
        f"- CI Gates found: {', '.join(snap['ci_gates_found']) or '—'}",
        "## Gaps"]

  if not issues:
    md.append("- ✅ No gaps detected.")
  else:
    for sev,msg in issues:
      md.append(f"- **{sev}** — {msg}")

  OUTD.joinpath("REALITY_TEST.md").write_text("\n".join(md), encoding="utf-8")

  # جدول فجوات للإدارة
  gaps = ["# GAPS_TABLE\n","| ID | Severity | Description | Action |","|---|---|---|---|"]
  for i,(sev,msg) in enumerate(issues,1):
    action = {
      "missing_frontend":"Initialize Next.js skeleton under src/frontend with TS & Tailwind.",
      "missing_backend":"Ensure FastAPI app with endpoints exists, or stub service.",
      "missing_db":"Add Postgres + Alembic migrations (or infra refs).",
      "low_tests":"Add unit/integration tests to reach baseline (≥5).",
      "missing_ci_gates":"Enable required workflows (gitleaks/CodeQL)."
    }.get(sev,"Investigate")
    gaps.append(f"| GAP-{i:02d} | {('HIGH' if sev in ['missing_backend','missing_db'] else 'MED')} | {msg} | {action} |")

  OUTD.joinpath("GAPS_TABLE.md").write_text("\n".join(gaps), encoding="utf-8")

def main():
  cfg = load_cfg()
  snap = reality_snapshot()
  issues = assess(snap, cfg)
  write_reports(snap, issues)

  hard = set(cfg.get("fail_on",[]))
  soft = set(cfg.get("soft_fail_on",[]))
  keys = [k for k,_ in issues]
  if any(k in hard for k in keys):
    print("❌ Reality Test: hard-fail gaps present. See reports/REALITY_TEST.*")
    sys.exit(1)
  if any(k in soft for k in keys):
    print("⚠️ Reality Test: soft-fail gaps present. See reports/REALITY_TEST.*")
    # لا نفشل البناء هنا
  print("✅ Reality Test passed.")
  return 0

if __name__ == "__main__":
  sys.exit(main())
