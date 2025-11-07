#!/usr/bin/env python3

import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)

def analyze_codebase():
    """تحليل قاعدة الكود"""
    langs_files = {}
    endpoints_count = 0
    tests_count = 0

    # فحص الملفات
    for root_dir, dirs, files in os.walk(ROOT):
        # تجاهل مجلدات معينة
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'htmlcov', 'dist']]

        for file in files:
            if file.endswith('.py'):
                langs_files['py'] = langs_files.get('py', 0) + 1
                file_path = Path(root_dir) / file

                try:
                    content = file_path.read_text(encoding='utf-8')

                    # عد النقاط النهائية
                    if '@app.' in content or '@router.' in content:
                        endpoints_count += len(re.findall(r'@(?:app|router)\.(?:get|post|put|delete|patch)', content))

                    # عد الاختبارات
                    if 'def test_' in content:
                        tests_count += len(re.findall(r'def test_', content))

                except:
                    pass

            elif file.endswith('.ts') or file.endswith('.tsx'):
                langs_files['ts'] = langs_files.get('ts', 0) + 1
            elif file.endswith('.js') or file.endswith('.jsx'):
                langs_files['js'] = langs_files.get('js', 0) + 1
            elif file.endswith('.dart'):
                langs_files['dart'] = langs_files.get('dart', 0) + 1

    return {
        "snapshot": {
            "langs_files": langs_files,
            "endpoints_count": endpoints_count,
            "tests_count": tests_count,
            "frontend": (ROOT / "src" / "frontend" / "package.json").exists(),
            "backend": (ROOT / "src" / "backend" / "main.py").exists(),
            "db": (ROOT / "src" / "backend" / "main.py").exists() and "sqlalchemy" in (ROOT / "pyproject.toml").read_text()
        }
    }

def main():
    results = analyze_codebase()

    # كتابة التقرير
    (OUT / "REALITY_TEST.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("✅ Reality Test completed")
    print(f"  - Languages: {results['snapshot']['langs_files']}")
    print(f"  - Frontend: {'✅' if results['snapshot']['frontend'] else '❌'}")
    print(f"  - Backend: {'✅' if results['snapshot']['backend'] else '❌'}")
    print(f"  - Endpoints: {results['snapshot']['endpoints_count']}")
    print(f"  - Tests: {results['snapshot']['tests_count']}")

if __name__ == "__main__":
    main()
