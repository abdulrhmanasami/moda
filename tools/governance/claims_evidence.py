#!/usr/bin/env python3

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)

def evaluate_claims():
    """تقييم المطالبات"""
    config_path = ROOT / "governance" / "claims.config.json"
    if not config_path.exists():
        return {"error": "claims.config.json not found"}

    claims_config = json.loads(config_path.read_text())

    results = {}
    hard_failures = []
    soft_failures = []

    for claim in claims_config["claims"]:
        claim_id = claim["id"]
        severity = claim["severity"]
        mode = claim.get("mode", "soft_fail")

        # تقييم المطالبة
        if claim_id == "FRONTEND_NEXTJS":
            passed = (ROOT / "src" / "frontend" / "package.json").exists()
        elif claim_id == "BACKEND_FASTAPI":
            passed = (ROOT / "src" / "backend" / "main.py").exists()
        elif claim_id == "DB_LAYER":
            passed = (ROOT / "src" / "backend" / "main.py").exists()
        elif claim_id == "TEST_COUNT_MIN":
            # نحتاج لقراءة REALITY_TEST.json
            reality_file = OUT / "REALITY_TEST.json"
            if reality_file.exists():
                reality = json.loads(reality_file.read_text())
                passed = reality.get("snapshot", {}).get("tests_count", 0) >= 10
            else:
                passed = False
        elif claim_id == "CLEAN_ROOT":
            # نحتاج لقراءة CLEAN_RELEASE_REPORT.json
            clean_file = OUT / "CLEAN_RELEASE_REPORT.json"
            if clean_file.exists():
                clean = json.loads(clean_file.read_text())
                passed = len(clean.get("root.illegal_files", [])) == 0 and len(clean.get("root.illegal_dirs", [])) == 0
            else:
                passed = False
        else:
            passed = False

        results[claim_id] = {
            "passed": passed,
            "severity": severity,
            "mode": mode
        }

        if not passed:
            if mode == "hard_fail":
                hard_failures.append(claim_id)
            else:
                soft_failures.append(claim_id)

    return {
        "claims": results,
        "hard_failures": hard_failures,
        "soft_failures": soft_failures,
        "overall_pass": len(hard_failures) == 0
    }

def main():
    results = evaluate_claims()

    # كتابة التقرير
    (OUT / "CLAIMS_EVIDENCE.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    if results["overall_pass"]:
        print("✅ Claims Evidence PASSED")
    else:
        print("❌ Claims Evidence FAILED:")
        if results["hard_failures"]:
            print(f"  Hard failures: {results['hard_failures']}")
        if results["soft_failures"]:
            print(f"  Soft failures: {results['soft_failures']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
