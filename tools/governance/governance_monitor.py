# @Study:ST-013
# @Study:ST-019
#!/usr/bin/env python3

# Placeholder v2: reads registry, scans repo for @Study tags, emits coverage.json

import json, re, sys, subprocess, pathlib

root = pathlib.Path('.')

studies = json.loads((root/'governance/studies/registry.json').read_text())['studies']

ids = {s['id'] for s in studies}

hits = set()

for p in root.rglob('*.*'):
    if p.is_file() and '.git' not in p.parts and p.suffix not in {'.png','.jpg','.jpeg','.pdf','.bin'}:
        try:
            txt = p.read_text(errors='ignore')
        except: 
            continue
        hits |= set(re.findall(r'@Study:(ST-[0-9]{3})', txt))

cov = round((len(hits & ids) / (len(ids) or 1)), 3)

out = {"total": cov, "hits": sorted(list(hits & ids)), "missing": sorted(list(ids - hits))}

(root/'governance/out').mkdir(parents=True, exist_ok=True)

(root/'governance/out/coverage.json').write_text(json.dumps(out, indent=2))

print(json.dumps(out))
