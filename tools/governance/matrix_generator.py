# @Study:ST-019
#!/usr/bin/env python3

# Matrix Generator: Create coverage matrix from registry.json

import json, pathlib

def generate_matrix():
    """Generate coverage matrix from registry"""
    
    root = pathlib.Path('.')
    registry_file = root / 'governance' / 'studies' / 'registry.json'
    
    if not registry_file.exists():
        print("❌ Registry not found")
        return
    
    registry = json.loads(registry_file.read_text())
    
    # Group studies by areas
    areas = {}
    for study in registry['studies']:
        for area in study['areas']:
            if area not in areas:
                areas[area] = []
            areas[area].append(study)
    
    # Generate matrix markdown
    matrix = f"""# Studies ↔ Code Coverage Matrix
## Auto-generated from registry.json

**Generated:** {registry['version']}
**Total Studies:** {len(registry['studies'])}

## Coverage by Area

"""
    
    for area, studies in areas.items():
        matrix += f"### {area.title()} ({len(studies)} studies)\n\n"
        matrix += "| Study ID | Title | Owners | Status |\n"
        matrix += "|----------|--------|--------|--------|\n"
        
        for study in studies:
            owners = ", ".join(study['owners'])
            status = "✅ Enforced" if study['enforced'] else "⚠️ Optional"
            title = study['title'][:50] + "..." if len(study['title']) > 50 else study['title']
            
            matrix += f"| {study['id']} | {title} | {owners} | {status} |\n"
        
        matrix += "\n"
    
    # Add implementation status section
    matrix += """## Implementation Status

### Current Status
- [ ] Registry populated
- [ ] @Study tags added to code
- [ ] CI gates active
- [ ] Coverage monitoring active

### Next Steps
1. Add @Study:ST-XXX tags to relevant code files
2. Run governance monitor to check coverage
3. Enable CI gates on main branch
4. Set up regular compliance reports

### Commands
```bash
# Check current coverage
python3 tools/governance_toolkit/governance_monitor.py

# Generate reports
python3 tools/governance_toolkit/governance_reporter.py

# Run compliance check
python3 tools/compliance/compliance_checker.py

# Check hygiene
bash tools/hygiene/repo_hygiene.sh
```
"""
    
    # Save matrix
    matrix_file = root / 'governance' / 'studies' / 'matrix.md'
    matrix_file.write_text(matrix)
    
    print(f"✅ Matrix generated: {matrix_file}")
    print(f"📊 Areas covered: {', '.join(areas.keys())}")

if __name__ == '__main__':
    generate_matrix()
