#!/usr/bin/env python3

import os, re, sys, json, fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTD = ROOT / "reports"; OUTD.mkdir(parents=True, exist_ok=True)
CFG  = ROOT / "governance" / "claims.config.json"

def load_json(path):
  p = OUTD / path
  if p.exists():
    try:
      return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
      return {}
  return {}

def list_files(pattern):
  return [str(p) for p in ROOT.rglob(pattern)]

def count_endpoints():
  c = 0
  for p in ROOT.rglob("*.py"):
    if "htmlcov" in str(p): continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    c += len(re.findall(r"@app\.(get|post|put|delete|patch)\(", t))
  return c

def has_frontend_next():
  pkg = ROOT / "src" / "frontend" / "package.json"
  if pkg.exists():
    try:
      data = json.loads(pkg.read_text(encoding="utf-8"))
      deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}  # Added ** to merge dictionaries
      if "next" in deps: return True
    except: pass
  for mark in ["next.config.js","next.config.ts","app","pages"]:
    if (ROOT / "src" / "frontend" / mark).exists(): return True
  return False

def has_db_layer():
  if (ROOT/"alembic.ini").exists(): return True
  if list((ROOT/"migrations").glob("**/*")): return True
  for p in ROOT.rglob("docker-compose*.y*ml"):
    try:
      if "postgres" in p.read_text(encoding="utf-8", errors="ignore").lower(): return True
    except: pass
  if list((ROOT/"infrastructure").glob("**/*.tf")): return True
  if list((ROOT/"infrastructure"/"helm").glob("**/*")): return True
  return False

def tests_count():
  pats = ["tests/**/*.py","**/*.spec.ts","**/*.spec.tsx","**/*.test.ts","**/*.test.tsx"]
  n = 0
  for pat in pats:
    n += len(list(ROOT.rglob(pat)))
  return n

def ci_gates():
  found = set()
  for w in (ROOT/".github"/"workflows").glob("*.yml"):
    txt = w.read_text(encoding="utf-8", errors="ignore").lower()
    if "gitleaks" in txt: found.add("gitleaks")
    if "codeql" in txt:
      found.add("CodeQL / Analyze (javascript-typescript)")
      found.add("CodeQL / Analyze (python)")
  return sorted(list(found))

def repo_megabytes():
  total = 0
  for p in ROOT.rglob("*"):
    if p.is_file():
      try: total += p.stat().st_size
      except: pass
  return round(total/1024/1024, 3)

def flatten(d, prefix=""):
  out = {}
  if isinstance(d, dict):
    for k,v in d.items():
      out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
  elif isinstance(d, list):
    for i,v in enumerate(d):
      out.update(flatten(v, f"{prefix}.{i}" if prefix else str(i)))
  else:
    out[prefix] = d
  return out

def get_path(d, key):
  cur = d
  for part in key.split("."):
    if isinstance(cur, list) and part.isdigit():
      idx = int(part)
      if idx < 0 or idx >= len(cur): return None
      cur = cur[idx]
    elif isinstance(cur, dict):
      if part not in cur: return None
      cur = cur[part]
    else:
      return None
  return cur

def eval_claim(claim):
  evid = {"ok": False, "actual": None, "evidence": {}}
  ev = claim["evaluator"]

  if ev == "frontend_nextjs":
    v = has_frontend_next()
    evid["ok"] = bool(v) == bool(claim.get("expect", True))
    evid["actual"] = v

  elif ev == "backend_endpoints_min":
    n = count_endpoints()
    evid["ok"] = n >= int(claim.get("expect_min", 1))
    evid["actual"] = n

  elif ev == "db_layer":
    v = has_db_layer()
    evid["ok"] = bool(v) == bool(claim.get("expect", True))
    evid["actual"] = v

  elif ev == "tests_min":
    n = tests_count()
    evid["ok"] = n >= int(claim.get("expect_min", 1))
    evid["actual"] = n

  elif ev == "ci_gates_superset":
    have = set(ci_gates())
    need = set(claim.get("expect_set", []))
    evid["ok"] = need.issubset(have)
    evid["actual"] = sorted(list(have))
    evid["evidence"]["missing"] = sorted(list(need - have))

  elif ev == "clean_release_report_zero":
    rep = load_json("CLEAN_RELEASE_REPORT.json")
    ok = True
    for path in claim.get("expect_from_report",{}).get("path_equals_zero",[]):
      val = get_path(rep, path)
      if val is None: ok = False
      elif isinstance(val, list) and len(val) != 0: ok = False
      elif isinstance(val, (int, float)) and val != 0: ok = False
    evid["ok"] = ok
    evid["actual"] = rep

  elif ev == "docmap_report_zero":
    rep = load_json("DOCMAP_SYNC.json")
    ok = True
    for path in claim.get("expect_from_report",{}).get("path_equals_zero",[]):
      val = get_path(rep, path)
      if val is None: ok = False
      elif isinstance(val, list) and len(val) != 0: ok = False
      elif isinstance(val, (int, float)) and val != 0: ok = False
    evid["ok"] = ok
    evid["actual"] = rep

  elif ev == "reality_flags_true":
    rep = load_json("REALITY_TEST.json")
    ok = True
    for path in claim.get("expect_from_report",{}).get("bool_true",[]):
      val = get_path(rep, path)
      if val is not True: ok = False
    evid["ok"] = ok
    evid["actual"] = rep.get("snapshot", {})

  elif ev == "file_exists":
    target = claim.get("expect")
    p = ROOT / target if target else None
    v = p.exists() if p else False
    evid["ok"] = v
    evid["actual"] = v

  elif ev == "repo_size_budget":
    mb = repo_megabytes()
    evid["ok"] = mb <= float(claim.get("expect_max_mb", 500))
    evid["actual"] = mb

  else:
    evid["ok"] = False
    evid["actual"] = f"Unknown evaluator: {ev}"

  return evid

def main():
  cfg = json.loads(CFG.read_text(encoding="utf-8")) if CFG.exists() else {"claims":[]}
  results = []
  hard_ids = set(cfg.get("hard_fail_ids", []))
  soft_ids = set(cfg.get("soft_fail_ids", []))
  hard_fail = False
  for cl in cfg["claims"]:
    ev = eval_claim(cl)
    rec = {
      "id": cl["id"], "desc": cl["desc"],
      "severity": cl["severity"], "ok": ev["ok"],
      "actual": ev["actual"], "evidence": ev.get("evidence", {})
    }
    results.append(rec)
    if not ev["ok"] and cl["id"] in hard_ids: hard_fail = True

  OUTD.joinpath("CLAIMS_EVIDENCE.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

  # Markdown report
  lines = [
    "# Claims ↔ Evidence Report",
    "| ID | Severity | Status | Actual |",
    "|---|---|---:|---|"
  ]
  for r in results:
    status = "✅ PASS" if r["ok"] else "❌ FAIL"
    lines.append(f"| {r['id']} | {r['severity']} | {status} | {str(r['actual'])[:120]} |")
  OUTD.joinpath("CLAIMS_EVIDENCE.md").write_text("\n".join(lines), encoding="utf-8")

  if hard_fail:
    print("❌ Claims Evidence: hard-fail claims missing evidence. See reports/CLAIMS_EVIDENCE.*")
    sys.exit(1)
  print("✅ Claims Evidence passed.")
  return 0

if __name__ == "__main__":
  sys.exit(main())
