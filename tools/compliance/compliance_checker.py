# @Study:ST-013
# @Study:ST-019
#!/usr/bin/env python3

# Placeholder: simple static checks for PII patterns and forbidden imports

import re, pathlib, sys

pii = re.compile(r'(email@|@gmail\.com|phone|iban|ssn|passport|national_id)', re.I)

forbidden = re.compile(r'(import\s+pickle|import\s+subprocess\s+as\s+sp)', re.I)

issues_found = []
files_checked = 0

for p in pathlib.Path('.').rglob('*.py'):
    if '.git' in p.parts: continue

    # Skip compliance checker itself and tools directory for now
    if 'compliance_checker.py' in str(p) or 'tools/' in str(p):
        continue

    files_checked += 1
    txt = p.read_text(errors='ignore')

    if pii.search(txt):
        issues_found.append(f"❌ PII pattern found in {p}")
    if forbidden.search(txt):
        issues_found.append(f"❌ Forbidden import found in {p}")

# Generate compliance report
with open('compliance_report.txt', 'w') as f:
    f.write("🔍 **Compliance Check Report**\n")
    f.write(f"- **Files Checked:** {files_checked}\n")
    f.write(f"- **Issues Found:** {len(issues_found)}\n")

    if issues_found:
        f.write("- **Status:** ❌ FAILED\n\n")
        f.write("### Issues:\n")
        for issue in issues_found:
            f.write(f"- {issue}\n")
    else:
        f.write("- **Status:** ✅ PASSED\n")
        f.write("- No compliance issues found\n")

# Print results
for issue in issues_found:
    print(issue)

if issues_found:
    print(f"\n❌ Compliance FAILED - {len(issues_found)} issues found")
    sys.exit(1)

print(f"✅ Compliance PASSED - {files_checked} files checked, 0 issues")
