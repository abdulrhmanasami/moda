#!/usr/bin/env python3

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)

def evaluate_drift():
    """تقييم الانحراف"""
    config_path = ROOT / "governance" / "drift_guard.config.json"
    if not config_path.exists():
        return {"error": "drift_guard.config.json not found"}

    config = json.loads(config_path.read_text())

    issues_hard = []
    issues_soft = []

    # قراءة التقارير
    reality_file = OUT / "REALITY_TEST.json"
    docmap_file = OUT / "DOCMAP_SYNC.json"

    if reality_file.exists():
        reality = json.loads(reality_file.read_text())
        snapshot = reality.get("snapshot", {})

        # فحص الحد الأدنى للنقاط النهائية
        endpoints = snapshot.get("endpoints_count", 0)
        if endpoints < config["hard_fail"]["endpoints_min"]:
            issues_hard.append(f"Endpoints below minimum: {endpoints} < {config['hard_fail']['endpoints_min']}")

        # فحص الحد الأدنى للاختبارات
        tests = snapshot.get("tests_count", 0)
        if tests < config["hard_fail"]["tests_min"]:
            issues_hard.append(f"Tests below minimum: {tests} < {config['hard_fail']['tests_min']}")

    if docmap_file.exists():
        docmap = json.loads(docmap_file.read_text())

        # فحص الملفات المفقودة
        missing = len(docmap.get("missing", []))
        if missing > config["hard_fail"]["doc_missing"]:
            issues_hard.append(f"Missing docs: {missing} > {config['hard_fail']['doc_missing']}")

        # فحص الملفات اليتيمة
        orphan = len(docmap.get("orphan", []))
        if orphan > config["hard_fail"]["doc_orphan"]:
            issues_hard.append(f"Orphan docs: {orphan} > {config['hard_fail']['doc_orphan']}")

    # فحص اللغات غير المعروفة (إذا كان مفعلاً)
    if config["hard_fail"]["unknown_langs"] and reality_file.exists():
        langs = snapshot.get("langs_files", {})
        known_langs = ["py", "ts", "js", "dart"]  # قائمة اللغات المعروفة
        unknown = [lang for lang in langs.keys() if lang not in known_langs]
        if unknown:
            issues_hard.append(f"Unknown languages: {unknown}")

    return {
        "issues_hard": issues_hard,
        "issues_soft": issues_soft,
        "overall_pass": len(issues_hard) == 0
    }

def main():
    results = evaluate_drift()

    # كتابة التقرير
    (OUT / "DRIFT_GUARD.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    if results["overall_pass"]:
        print("✅ Drift Guard PASSED")
    else:
        print("❌ Drift Guard FAILED:")
        for issue in results["issues_hard"]:
            print(f"  - {issue}")
        sys.exit(1)

if __name__ == "__main__":
    main()
