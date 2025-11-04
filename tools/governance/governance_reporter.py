# @Study:ST-019
#!/usr/bin/env python3

# Governance Reporter v2: Generates executive and technical reports

import json, pathlib, datetime
from typing import Dict, Any

def generate_reports():
    """Generate executive and technical governance reports"""
    
    root = pathlib.Path('.')
    
    # Load data
    coverage = json.loads((root/'governance/out/coverage.json').read_text())
    
    # Generate executive report
    exec_report = f"""# تقرير الحوكمة التنفيذي
## {datetime.date.today()}

### المقاييس الرئيسية
- تغطية الدراسات: {coverage['total']:.1%}
- عدد الدراسات المغطاة: {len(coverage['hits'])}
- عدد الدراسات المفقودة: {len(coverage['missing'])}

### الوضع العام
{'✅ امتثال جيد' if coverage['total'] >= 0.8 else '⚠️ يحتاج تحسين'}

### الدراسات المفقودة
{chr(10).join(f'- {s}' for s in coverage['missing'])}
"""

    # Generate technical report
    tech_report = f"""# تقرير الحوكمة التقني
## {datetime.date.today()}

### تحليل التغطية
```json
{json.dumps(coverage, indent=2, ensure_ascii=False)}
```

### التوصيات الفنية
- أضف وسوم @Study للملفات المفقودة
- راجع registry.json للتحقق من الدراسات
- نفذ CI gates لمنع الانحرافات

### حالة الامتثال
{'PASS' if coverage['total'] >= 0.8 else 'FAIL'}
"""

    # Save reports
    out_dir = root / 'governance' / 'out'
    out_dir.mkdir(exist_ok=True)
    
    (out_dir / 'executive_report.md').write_text(exec_report)
    (out_dir / 'tech_report.md').write_text(tech_report)
    
    print("✅ تم توليد التقارير")
    print(f"📄 تقرير تنفيذي: governance/out/executive_report.md")
    print(f"📄 تقرير تقني: governance/out/tech_report.md")

if __name__ == '__main__':
    generate_reports()
