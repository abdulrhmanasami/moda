import json, os, sys
from pathlib import Path

cfg_p = Path("governance/budget.sentinel.config.json")
cfg = json.loads(cfg_p.read_text(encoding="utf-8"))

# مصادر البيانات:
# 1) متغير سرّي BUDGET_SNAPSHOT_JSON (JSON string)
# 2) ملف من env BUDGET_SNAPSHOT_FILE (default reports/finance/costs.json)

snap_json = os.getenv("BUDGET_SNAPSHOT_JSON")
snap_file = os.getenv("BUDGET_SNAPSHOT_FILE", "reports/finance/costs.json")

if snap_json:
    try:
        snap = json.loads(snap_json)
    except Exception as e:
        print(f"Invalid BUDGET_SNAPSHOT_JSON: {e}")
        sys.exit(1)
else:
    p = Path(snap_file)
    snap = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

issues_hard, issues_soft = [], []

def hf(key, actual, limit):
    issues_hard.append({"key": key, "actual": actual, "limit": limit})

def sf(key, note):
    issues_soft.append({"key": key, "note": note})

gpu = api = storage = 0.0
if snap is None:
    sf("missing_snapshot", "No cost snapshot provided.")
else:
    gpu     = float(snap.get("gpu_usd", 0.0))
    api     = float(snap.get("api_usd", 0.0))
    storage = float(snap.get("storage_usd", 0.0))

if gpu     > cfg["budgets"]["gpu_usd_max"]:     hf("gpu", gpu, cfg["budgets"]["gpu_usd_max"])
if api     > cfg["budgets"]["api_usd_max"]:     hf("api", api, cfg["budgets"]["api_usd_max"])
if storage > cfg["budgets"]["storage_usd_max"]: hf("storage", storage, cfg["budgets"]["storage_usd_max"])

# Error budget: نقرأ من Runtime Guard إن وجد، أو من ENV
err_pct = None
rt_p = Path("reports/RUNTIME_GUARD.json")
if rt_p.exists():
    try:
        rt = json.loads(rt_p.read_text(encoding="utf-8"))
        err_pct = float(rt.get("metrics", {}).get("error_rate_pct", None))
    except Exception:
        err_pct = None
if err_pct is None:
    if os.getenv("ERROR_RATE_PCT"):
        try: err_pct = float(os.getenv("ERROR_RATE_PCT"))
        except: err_pct = None

if err_pct is None:
    # إذا ما في بيانات، منعتبرها 0 (ضمن التحضير)
    err_pct = 0.0

allowed = float(cfg["error_budget"]["allowed_error_pct"])
if err_pct > allowed:
    hf("error_budget", err_pct, allowed)

report = {
  "period": cfg["period"],
  "budgets": {
    "limits": cfg["budgets"],
    "actuals": {"gpu_usd": gpu, "api_usd": api, "storage_usd": storage}
  },
  "error_budget": {
    "window_days": cfg["error_budget"]["window_days"],
    "allowed_error_pct": allowed,
    "actual_error_pct": round(err_pct, 3)
  },
  "issues_hard": issues_hard,
  "issues_soft": issues_soft,
  "sources": {
    "snapshot_file": snap_file if snap_json is None else "BUDGET_SNAPSHOT_JSON",
    "runtime_guard": rt_p.exists()
  }
}

Path("reports").mkdir(exist_ok=True)
Path("reports/BUDGET_SENTINEL.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
Path("reports/BUDGET_SENTINEL.md").write_text(
    "# Budget Sentinel Report\n\n"
    f"**Period:** {report['period']}\n\n"
    "## Cost\n"
    f"- GPU: ${gpu:.2f} (max ${cfg['budgets']['gpu_usd_max']:.2f})\n"
    f"- API: ${api:.2f} (max ${cfg['budgets']['api_usd_max']:.2f})\n"
    f"- Storage: ${storage:.2f} (max ${cfg['budgets']['storage_usd_max']:.2f})\n\n"
    "## Error Budget\n"
    f"- Allowed: {allowed:.2f}%\n"
    f"- Actual : {err_pct:.2f}%\n\n"
    f"## Hard Issues\n```json\n{json.dumps(issues_hard, indent=2)}\n```\n\n"
    f"## Soft Issues\n```json\n{json.dumps(issues_soft, indent=2)}\n```\n",
    encoding="utf-8"
)

if issues_hard:
    print("❌ Budget Sentinel: hard violations. See reports/BUDGET_SENTINEL.*")
    sys.exit(1)
elif issues_soft:
    print("⚠️ Budget Sentinel: soft warnings. See reports/BUDGET_SENTINEL.*")
    sys.exit(0)
else:
    print("✅ Budget Sentinel passed.")
    sys.exit(0)
