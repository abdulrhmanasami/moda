# @Study:ST-013
# @Study:ST-019
#!/usr/bin/env python3

# Placeholder: simple static checks for PII patterns and forbidden imports

import re, pathlib, sys

pii = re.compile(r'(email@|@gmail\.com|phone|iban|ssn|passport|national_id)', re.I)

forbidden = re.compile(r'(import\s+pickle|import\s+subprocess\s+as\s+sp)', re.I)

fail = False

for p in pathlib.Path('.').rglob('*.py'):
    if '.git' in p.parts: continue
    
    # Skip compliance checker itself and tools directory for now
    if 'compliance_checker.py' in str(p) or 'tools/' in str(p):
        continue
    
    txt = p.read_text(errors='ignore')
    if pii.search(txt) or forbidden.search(txt):
        print(f"❌ Compliance issue in {p}")
        fail = True

if fail:
    sys.exit(1)

print("✅ Compliance PASS")
