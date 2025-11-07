import json, sys
from pathlib import Path

cfg = json.loads(Path("governance/runtime.guard.config.json").read_text(encoding="utf-8"))
perf_p = Path("reports/runtime/perf.json")
perf = json.loads(perf_p.read_text(encoding="utf-8")) if perf_p.exists() else {"total":0,"ok":0,"err":0,"p95":0,"p99":0,"rps":0}

total, ok, err = perf.get("total",0), perf.get("ok",0), perf.get("err",0)
success_rate = (ok/total*100.0) if total else 100.0
error_rate = (err/total*100.0) if total else 0.0
p95 = perf.get("p95", 0)
p99 = perf.get("p99", 0)
rps = perf.get("rps", 0.0)

slos = cfg["slos"]
issues_hard, issues_soft = [], []

def chk(cond, key, actual, limit, kind="max"):
    msg = {"key": key, "actual": actual, "limit": limit, "type": kind}
    tgt = cfg["hard_fail"] if key in cfg["hard_fail"] else cfg["soft_fail"]
    if not cond:
        (issues_hard if key in cfg["hard_fail"] else issues_soft).append(msg)

chk(success_rate >= slos["success_rate_min_pct"], "success_rate", round(success_rate,2), slos["success_rate_min_pct"], "min")
chk(error_rate <= slos["error_rate_max_pct"],   "error_rate",   round(error_rate,2),   slos["error_rate_max_pct"],   "max")
chk(p95        <= slos["p95_latency_ms_max"],   "p95_latency",  p95,                    slos["p95_latency_ms_max"],   "max")
chk(p99        <= slos["p99_latency_ms_max"],   "p99_latency",  p99,                    slos["p99_latency_ms_max"],   "max")
chk(rps        >= slos["min_rps_ci"],           "rps_ci",       rps,                    slos["min_rps_ci"],           "min")

report = {
  "env": cfg["env"],
  "metrics": {"success_rate_pct": round(success_rate,2), "error_rate_pct": round(error_rate,2), "p95_ms": p95, "p99_ms": p99, "rps": rps},
  "issues_hard": issues_hard,
  "issues_soft": issues_soft
}
Path("reports").mkdir(exist_ok=True)
Path("reports/RUNTIME_GUARD.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
Path("reports/RUNTIME_GUARD.md").write_text(
    f"# Runtime Guard Report\n\n"
    f"- success_rate: {report['metrics']['success_rate_pct']}% (min {slos['success_rate_min_pct']}%)\n"
    f"- error_rate  : {report['metrics']['error_rate_pct']}% (max {slos['error_rate_max_pct']}%)\n"
    f"- p95         : {p95} ms (max {slos['p95_latency_ms_max']} ms)\n"
    f"- p99         : {p99} ms (max {slos['p99_latency_ms_max']} ms)\n"
    f"- rps (ci)    : {rps} (min {slos['min_rps_ci']})\n\n"
    f"## Hard Issues\n{json.dumps(issues_hard, indent=2)}\n\n## Soft Issues\n{json.dumps(issues_soft, indent=2)}\n",
    encoding="utf-8"
)

if issues_hard:
    print("❌ Runtime Guard: hard SLO violations. See reports/RUNTIME_GUARD.*")
    sys.exit(1)
elif issues_soft:
    print("⚠️ Runtime Guard: soft SLO warnings. See reports/RUNTIME_GUARD.*")
else:
    print("✅ Runtime Guard passed.")
