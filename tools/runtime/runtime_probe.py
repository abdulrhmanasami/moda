import asyncio, json, statistics, time
from pathlib import Path

# محاولة استيراد تطبيق FastAPI
app = None
for cand in ("src.backend.main", "src.backend.app", "src.backend.api"):
    try:
        mod = __import__(cand, fromlist=["app"])
        app = getattr(mod, "app", None)
        if app:
            break
    except Exception:
        pass

if app is None:
    # ما في تطبيق — نخرج ببيانات افتراضية آمنة
    Path("reports/runtime").mkdir(parents=True, exist_ok=True)
    data = {"total": 0, "ok": 0, "err": 0, "latencies_ms": [], "p95": 0, "p99": 0, "rps": 0.0}
    Path("reports/runtime/perf.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("No FastAPI app found; wrote empty perf.json")
    raise SystemExit(0)

try:
    import httpx
except Exception:
    raise SystemExit("httpx غير مُثبت. ثبّته في الـ workflow: pip install httpx[http2]")

ROUTES_CAND = ["/", "/health", "/status", "/docs", "/openapi.json"]
CONCURRENCY = 20
REQUESTS_PER_ROUTE = 25

async def run():
    latencies = []
    ok = err = 0
    start = time.perf_counter()
    async with httpx.AsyncClient(app=app, base_url="http://testserver", timeout=5.0) as client:
        async def hit(path):
            nonlocal ok, err
            t0 = time.perf_counter()
            try:
                r = await client.get(path)
                ok += 1 if r.status_code < 500 else 0
                err += 1 if r.status_code >= 500 else 0
                latencies.append((time.perf_counter() - t0) * 1000.0)
            except Exception:
                err += 1

        tasks = []
        for route in ROUTES_CAND:
            for _ in range(REQUESTS_PER_ROUTE):
                tasks.append(hit(route))
        # تنفيذ متحكم بالتوازي
        for i in range(0, len(tasks), CONCURRENCY):
            batch = tasks[i:i+CONCURRENCY]
            await asyncio.gather(*batch)

    dur = time.perf_counter() - start
    total = ok + err
    p95 = statistics.quantiles(latencies, n=100)[94] if latencies else 0
    p99 = statistics.quantiles(latencies, n=100)[98] if latencies else 0
    rps = total / dur if dur > 0 else 0.0
    out = {
        "total": total, "ok": ok, "err": err,
        "latencies_ms": [],  # لا نخزن قائمة كاملة لتخفيف الحجم
        "p95": round(p95, 2), "p99": round(p99, 2), "rps": round(rps, 2),
        "duration_s": round(dur, 3)
    }
    Path("reports/runtime").mkdir(parents=True, exist_ok=True)
    Path("reports/runtime/perf.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))

asyncio.run(run())
