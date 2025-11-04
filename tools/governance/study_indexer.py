# @Study:ST-007
# @Study:ST-005
# @Study:ST-002
# @Study:ST-019
#!/usr/bin/env python3

# Study Indexer: Automatically populate registry.json with existing studies

import json, hashlib, pathlib, re
from datetime import date

def index_studies():
    """Index all studies and populate registry.json"""
    
    root = pathlib.Path('.')
    studies_dir = root / 'studies'
    
    if not studies_dir.exists():
        print("❌ Studies directory not found")
        return
    
    studies = []
    study_id = 1
    
    # Index master studies
    master_dir = studies_dir / 'master_studies'
    if master_dir.exists():
        for file_path in sorted(master_dir.glob('*.md')):
            if file_path.name in ['MODAMODA_INVISIBLE_MANNEQUIN_MASTER_STUDY.md', 
                                  'TECHNICAL_SPECIFICATION.md', 
                                  'DEVELOPMENT_ROADMAP.md', 
                                  'BUSINESS_ANALYSIS.md']:
                study = create_study_entry(file_path, f"ST-{study_id:03d}", "master")
                studies.append(study)
                study_id += 1
    
    # Index business analysis
    biz_dir = studies_dir / 'business_analysis'
    if biz_dir.exists():
        for file_path in sorted(biz_dir.glob('*.md')):
            if 'market' in file_path.name.lower() or 'operational' in file_path.name.lower():
                study = create_study_entry(file_path, f"ST-{study_id:03d}", "business")
                studies.append(study)
                study_id += 1
    
    # Index technical specs
    tech_dir = studies_dir / 'technical_specs'
    if tech_dir.exists():
        for file_path in sorted(tech_dir.glob('*.md')):
            study = create_study_entry(file_path, f"ST-{study_id:03d}", "technical")
            studies.append(study)
            study_id += 1
    
    # Index implementation phases
    impl_dir = studies_dir / 'implementation_phases'
    if impl_dir.exists():
        for file_path in sorted(impl_dir.glob('*.md')):
            study = create_study_entry(file_path, f"ST-{study_id:03d}", "implementation")
            studies.append(study)
            study_id += 1
    
    # Index compliance
    comp_dir = studies_dir / 'compliance_governance'
    if comp_dir.exists():
        for file_path in sorted(comp_dir.glob('*.md')):
            study = create_study_entry(file_path, f"ST-{study_id:03d}", "compliance")
            studies.append(study)
            study_id += 1
    
    # Save registry
    registry = {
        "version": date.today().isoformat(),
        "studies": studies
    }
    
    registry_file = root / 'governance' / 'studies' / 'registry.json'
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    registry_file.write_text(json.dumps(registry, indent=2, ensure_ascii=False))
    
    print(f"✅ Indexed {len(studies)} studies")
    print(f"📄 Registry saved: {registry_file}")

def create_study_entry(file_path: pathlib.Path, study_id: str, category: str) -> dict:
    """Create a study entry from file path"""
    
    # Read file content
    content = file_path.read_text(encoding='utf-8')
    
    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem.replace('_', ' ')
    
    # Calculate SHA256
    sha256 = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # Determine owners and areas based on category
    owners_map = {
        "master": ["@ceo", "@cto", "@cpo"],
        "business": ["@cfo", "@ceo"],
        "technical": ["@cto", "@technology-committee"],
        "implementation": ["@cpo", "@technology-committee"],
        "compliance": ["@legal", "@security", "@quality-committee"]
    }
    
    areas_map = {
        "master": ["architecture", "operations", "finance"],
        "business": ["finance", "operations"],
        "technical": ["architecture", "ai-ethics", "security"],
        "implementation": ["operations", "testing"],
        "compliance": ["security", "ai-ethics", "compliance"]
    }
    
    return {
        "id": study_id,
        "title": title,
        "rev": "v1.0",
        "sha256": sha256,
        "enforced": True,
        "owners": owners_map.get(category, ["@governance"]),
        "areas": areas_map.get(category, ["operations"])
    }

if __name__ == '__main__':
    index_studies()
