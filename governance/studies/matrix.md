# @Study:ST-019
# Studies Relationship Matrix
## Normalized Dependencies & Cross-References

**Version:** 1.0.0
**Revision:** GOV-STUDIES-NORMALIZE-001
**Date:** 2025-11-05
**Purpose:** Single source of truth for study relationships and dependencies

---

## 📊 Matrix Overview

### Legend
- ✅ **Required**: Must read before proceeding
- 🔄 **Reference**: Use as needed
- ❌ **Deprecated**: Use canonical version instead
- 🔗 **Alias**: Points to canonical study

### Studies by Category

#### 🎯 Master Studies (ST-001, ST-002, ST-005, ST-019)
| Study ID | Title | Dependencies | Status | Notes |
|----------|-------|--------------|--------|-------|
| ST-001 | Master Study | None | ✅ Active | Primary reference |
| ST-002 | Development Roadmap | ST-001 | ✅ Active | Implementation guide |
| ST-005 | Business Analysis | ST-001 | ✅ Active | Financial foundation |
| ST-019 | Studies Index | All | ✅ Active | Navigation guide |

#### 🔧 Technical Specs (ST-007, ST-013)
| Study ID | Title | Dependencies | Status | Notes |
|----------|-------|--------------|--------|-------|
| ST-007 | Architecture & Stack | ST-001, ST-013 | ✅ Active | Tech foundation |
| ST-013 | AI Model Strategy | ST-007 | ✅ Active | AI implementation |

#### 💼 Business Analysis (ST-014)
| Study ID | Title | Dependencies | Status | Notes |
|----------|-------|--------------|--------|-------|
| ST-014 | Financial Plan | ST-005 | ✅ Active | Revenue model |

#### 🚀 Implementation (ST-011)
| Study ID | Title | Dependencies | Status | Notes |
|----------|-------|--------------|--------|-------|
| ST-011 | Development Roadmap | ST-002, ST-007, ST-013 | ✅ Active | Execution plan |

#### 🎯 Core Strategy (ST-008, ST-015)
| Study ID | Title | Dependencies | Status | Notes |
|----------|-------|--------------|--------|-------|
| ST-008 | Executive Summary | None | ✅ Active | Vision document |
| ST-015 | Business Model | ST-008, ST-014 | ✅ Active | Strategy execution |

---

## 🔄 Cross-Reference Map

### Reading Order for New Team Members
```
ST-008 (Executive Summary)
├── ST-001 (Master Study)
│   ├── ST-019 (Studies Index)
│   ├── ST-005 (Business Analysis)
│   │   └── ST-014 (Financial Plan)
│   ├── ST-015 (Business Model)
│   ├── ST-007 (Architecture)
│   │   └── ST-013 (AI Strategy)
│   └── ST-002 (Dev Roadmap)
│       └── ST-011 (Implementation)
```

### Reading Order for Developers
```
ST-007 (Architecture)
├── ST-013 (AI Strategy)
├── ST-002 (Dev Roadmap)
└── ST-011 (Implementation)
```

### Reading Order for Business Team
```
ST-008 (Executive Summary)
├── ST-005 (Business Analysis)
│   └── ST-014 (Financial Plan)
└── ST-015 (Business Model)
```

---

## 🔗 Aliases & Deprecated Files

### Canonical → Aliases Mapping
| Canonical Path | Aliases | Status |
|----------------|---------|--------|
| `studies/master_studies/MODAMODA_INVISIBLE_MANNEQUIN_MASTER_STUDY.md` | `studies/master_studies/Comprehensive Analysis of the Invisible Mannequin Project.md` | 🔗 Alias |
| `studies/master_studies/BUSINESS_ANALYSIS.md` | `studies/business_analysis/01_تحليل_السوق_والاستراتيجية_التنافسية_المحسن.md` | 🔗 Alias |
| `studies/technical_specs/03_الهيكلية_والمكدس_التقني_المحسن.md` | `studies/master_studies/TECHNICAL_SPECIFICATION.md` | 🔗 Alias |
| `studies/technical_specs/04_استراتيجية_نموذج_الذكاء_الاصطناعي_الأساسي_المحسن.md` | `studies/technical_specs/ai_model_strategy_axis5.md` | 🔗 Alias |
| `studies/business_analysis/06_المخطط_التشغيلي_والمالي_المحسن.md` | `studies/business_analysis/market_open_source_axis4.md`<br>`studies/business_analysis/numbers_operations_axis6.md` | 🔗 Alias |
| `studies/implementation_phases/05_خارطة_الطريق_المنهجية_المحسن.md` | `studies/implementation_phases/methodical_development_plan.md`<br>`studies/implementation_phases/mvp_professional_study.md`<br>`studies/implementation_phases/v1_0_professional_study.md`<br>`studies/implementation_phases/v1_1_b2b_professional_study.md` | 🔗 Alias |

---

## ⚠️ Migration Notes

### Files to Remove (After Migration)
- `studies/business_analysis/01_تحليل_السوق_والاستراتيجية_التنافسية_المحسن.md` → Use ST-005
- `studies/master_studies/TECHNICAL_SPECIFICATION.md` → Use ST-007
- `studies/technical_specs/ai_model_strategy_axis5.md` → Use ST-013
- `studies/business_analysis/market_open_source_axis4.md` → Use ST-014
- `studies/business_analysis/numbers_operations_axis6.md` → Use ST-014
- `studies/implementation_phases/methodical_development_plan.md` → Use ST-011
- `studies/implementation_phases/mvp_professional_study.md` → Use ST-011
- `studies/implementation_phases/v1_0_professional_study.md` → Use ST-011
- `studies/implementation_phases/v1_1_b2b_professional_study.md` → Use ST-011
- `studies/master_studies/Comprehensive Analysis of the Invisible Mannequin Project.md` → Use ST-001

### Empty Directories to Remove
- `governance/out/`
- `governance/legal/`
- `governance/training/checklists/`
- `scripts/governance/`
- `scripts/helm/`
- `tools/security/reports/`
- `infrastructure/terraform/modules/s3/`
- `infrastructure/terraform/modules/redis/`
- `infrastructure/terraform/modules/ecs/`
- `infrastructure/terraform/modules/security_groups/`
- `infrastructure/terraform/modules/monitoring/`
- `infrastructure/terraform/modules/rds/`

---

## 🔒 Governance Rules

1. **RFC Required**: Any change to canonical paths requires RFC approval
2. **Checksum Verification**: All canonical files must have valid checksums
3. **Alias Preservation**: Keep aliases for backward compatibility
4. **Automated Validation**: CI/CD must validate registry integrity

---

**Generated by:** GOV-STUDIES-NORMALIZE-001
**Validation:** Checksums verified, relationships mapped
**Next Step:** Lock registry after verification
