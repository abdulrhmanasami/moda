# @Study:ST-011
# @Study:ST-002
# @Study:ST-019
#!/usr/bin/env python3
"""
نظام مراقبة الحوكمة التلقائي - Governance Monitor System
يضمن الامتثال الكامل للدراسات والحوكمة في جميع مراحل المشروع
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/governance_monitor.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class GovernanceMonitor:
    """
    نظام مراقبة الحوكمة الشامل والتلقائي
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.studies_path = self.project_root / "studies"
        self.governance_path = self.project_root / "governance" / "active"
        self.logs_path = self.project_root / "logs"
        self.logs_path.mkdir(exist_ok=True)

        # تحميل البيانات الأساسية
        self.studies_index = self._load_studies_index()
        self.governance_framework = self._load_governance_framework()

        # إعداد المقاييس
        self.metrics = {
            "compliance_score": 0,
            "last_check": None,
            "alerts": [],
            "recommendations": [],
        }

    def _load_studies_index(self) -> Dict[str, Any]:
        """تحميل فهرس الدراسات"""
        index_file = self.studies_path / "MASTER_STUDIES_INDEX.md"
        if not index_file.exists():
            logger.warning(f"Studies index not found: {index_file}")
            return {}

        # تحليل الملف واستخراج الروابط
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        # استخراج المعلومات الأساسية (يمكن تحسين هذا التحليل)
        return {
            "path": str(index_file),
            "last_modified": datetime.fromtimestamp(index_file.stat().st_mtime),
            "content_hash": hash(content),
        }

    def _load_governance_framework(self) -> Dict[str, Any]:
        """تحميل إطار العمل الحوكمي"""
        framework_file = self.governance_path / "GOVERNANCE_FRAMEWORK.md"
        if not framework_file.exists():
            logger.warning(f"Governance framework not found: {framework_file}")
            return {}

        with open(framework_file, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "path": str(framework_file),
            "last_modified": datetime.fromtimestamp(framework_file.stat().st_mtime),
            "content_hash": hash(content),
        }

    def run_compliance_check(self) -> Dict[str, Any]:
        """
        تشغيل فحص شامل للامتثال
        """
        logger.info("Starting comprehensive compliance check...")

        results = {
            "timestamp": datetime.now(),
            "overall_score": 0,
            "categories": {},
            "alerts": [],
            "recommendations": [],
        }

        # فحص امتثال الكود
        code_compliance = self._check_code_compliance()
        results["categories"]["code"] = code_compliance

        # فحص امتثال التوثيق
        docs_compliance = self._check_documentation_compliance()
        results["categories"]["documentation"] = docs_compliance

        # فحص امتثال الأمان
        security_compliance = self._check_security_compliance()
        results["categories"]["security"] = security_compliance

        # فحص امتثال الدراسات
        studies_compliance = self._check_studies_compliance()
        results["categories"]["studies"] = studies_compliance

        # حساب النتيجة الإجمالية
        results["overall_score"] = self._calculate_overall_score(results["categories"])

        # توليد التنبيهات والتوصيات
        results["alerts"] = self._generate_alerts(results)
        results["recommendations"] = self._generate_recommendations(results)

        # حفظ النتائج
        self._save_results(results)

        logger.info(
            f"Compliance check completed with score: {results['overall_score']}%"
        )

        return results

    def _check_code_compliance(self) -> Dict[str, Any]:
        """فحص امتثال الكود للدراسات"""
        src_path = self.project_root / "src"

        if not src_path.exists():
            return {
                "score": 0,
                "status": "NOT_STARTED",
                "issues": ["Source code directory does not exist"],
                "details": {},
            }

        # فحص هيكل الكود
        structure_score = self._check_code_structure(src_path)

        # فحص استخدام التقنيات المحددة
        tech_score = self._check_technology_usage(src_path)

        # فحص جودة الكود
        quality_score = self._check_code_quality(src_path)

        overall_score = (structure_score + tech_score + quality_score) / 3

        return {
            "score": overall_score,
            "status": "GOOD" if overall_score >= 80 else "NEEDS_IMPROVEMENT",
            "structure_score": structure_score,
            "technology_score": tech_score,
            "quality_score": quality_score,
            "details": {
                "structure_check": structure_score,
                "technology_check": tech_score,
                "quality_check": quality_score,
            },
        }

    def _check_code_structure(self, src_path: Path) -> float:
        """فحص هيكل الكود"""
        required_dirs = ["backend", "frontend", "shared"]
        existing_dirs = [d.name for d in src_path.iterdir() if d.is_dir()]

        matched_dirs = len(set(required_dirs) & set(existing_dirs))
        score = (matched_dirs / len(required_dirs)) * 100

        return score

    def _check_technology_usage(self, src_path: Path) -> float:
        """فحص استخدام التقنيات المحددة في الدراسات"""
        # فحص وجود FastAPI في backend
        backend_path = src_path / "backend"
        fastapi_score = 50  # افتراضي

        if backend_path.exists():
            # البحث عن ملفات FastAPI
            fastapi_files = list(backend_path.glob("**/*.py"))
            if any("fastapi" in str(f) for f in fastapi_files):
                fastapi_score = 100

        # فحص وجود React/Next.js في frontend
        frontend_path = src_path / "frontend"
        frontend_score = 50  # افتراضي

        if frontend_path.exists():
            package_json = frontend_path / "package.json"
            if package_json.exists():
                with open(package_json, "r") as f:
                    try:
                        data = json.load(f)
                        if "next" in str(data).lower():
                            frontend_score = 100
                    except:
                        pass

        return (fastapi_score + frontend_score) / 2

    def _check_code_quality(self, src_path: Path) -> float:
        """فحص جودة الكود"""
        # فحص وجود ملفات الاختبار
        tests_path = self.project_root / "tests"
        test_score = 100 if tests_path.exists() else 0

        # فحص وجود ملفات التكوين
        config_files = ["pyproject.toml", "docker-compose.yml", "Dockerfile"]
        config_score = sum(1 for f in config_files if (self.project_root / f).exists())
        config_score = (config_score / len(config_files)) * 100

        return (test_score + config_score) / 2

    def _check_documentation_compliance(self) -> Dict[str, Any]:
        """فحص امتثال التوثيق"""
        docs_path = self.project_root / "docs"

        if not docs_path.exists():
            return {
                "score": 0,
                "status": "MISSING",
                "issues": ["Documentation directory does not exist"],
                "details": {},
            }

        # فحص وجود مجلدات التوثيق المطلوبة
        required_docs = ["api", "architecture", "deployment"]
        existing_docs = [d.name for d in docs_path.iterdir() if d.is_dir()]

        doc_coverage = len(set(required_docs) & set(existing_docs))
        score = (doc_coverage / len(required_docs)) * 100

        return {
            "score": score,
            "status": "GOOD" if score >= 70 else "INCOMPLETE",
            "coverage": f"{doc_coverage}/{len(required_docs)}",
            "details": {
                "existing_docs": existing_docs,
                "missing_docs": list(set(required_docs) - set(existing_docs)),
            },
        }

    def _check_security_compliance(self) -> Dict[str, Any]:
        """فحص امتثال الأمان"""
        # فحص وجود ملفات الأمان
        security_files = [".gitignore", "pyproject.toml"]
        security_score = sum(
            1 for f in security_files if (self.project_root / f).exists()
        )
        security_score = (security_score / len(security_files)) * 100

        # فحص إعدادات الأمان في التكوين
        config_security = 0
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            with open(pyproject_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "cryptography" in content or "bcrypt" in content:
                    config_security = 100

        overall_score = (security_score + config_security) / 2

        return {
            "score": overall_score,
            "status": "SECURE" if overall_score >= 80 else "NEEDS_SECURITY_REVIEW",
            "details": {
                "security_files": security_score,
                "security_config": config_security,
            },
        }

    def _check_studies_compliance(self) -> Dict[str, Any]:
        """فحص امتثال الدراسات"""
        if not self.studies_index:
            return {
                "score": 0,
                "status": "NO_STUDIES_INDEX",
                "issues": ["Studies index not found"],
                "details": {},
            }

        # فحص وجود ملفات الدراسات الأساسية
        master_studies_path = self.studies_path / "master_studies"
        required_files = [
            "MODAMODA_INVISIBLE_MANNEQUIN_MASTER_STUDY.md",
            "TECHNICAL_SPECIFICATION.md",
            "DEVELOPMENT_ROADMAP.md",
            "BUSINESS_ANALYSIS.md",
        ]

        existing_files = [
            f.name for f in master_studies_path.glob("*.md") if f.is_file()
        ]
        matched_files = len(set(required_files) & set(existing_files))
        score = (matched_files / len(required_files)) * 100

        return {
            "score": score,
            "status": "COMPLETE" if score == 100 else "INCOMPLETE",
            "coverage": f"{matched_files}/{len(required_files)}",
            "details": {
                "existing_files": existing_files,
                "missing_files": list(set(required_files) - set(existing_files)),
            },
        }

    def _calculate_overall_score(self, categories: Dict[str, Dict]) -> float:
        """حساب النتيجة الإجمالية"""
        if not categories:
            return 0

        total_score = sum(cat.get("score", 0) for cat in categories.values())
        return total_score / len(categories)

    def _generate_alerts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """توليد التنبيهات الذكية"""
        alerts = []

        # تنبيهات حرجة
        if results["overall_score"] < 60:
            alerts.append(
                {
                    "level": "CRITICAL",
                    "type": "OVERALL_COMPLIANCE",
                    "message": f'Overall compliance score is critically low: {results["overall_score"]:.1f}%',
                    "action_required": "Immediate governance review required",
                }
            )

        # تنبيهات للفئات الفردية
        for category, data in results["categories"].items():
            score = data.get("score", 0)

            if score < 50:
                alerts.append(
                    {
                        "level": "HIGH",
                        "type": f"{category.upper()}_COMPLIANCE",
                        "message": f"{category.title()} compliance is below acceptable level: {score:.1f}%",
                        "action_required": f"Review and fix {category} compliance issues",
                    }
                )

        return alerts

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """توليد التوصيات الذكية"""
        recommendations = []

        # توصيات عامة
        if results["overall_score"] < 80:
            recommendations.append("Schedule immediate governance review meeting")
            recommendations.append("Prioritize fixing critical compliance gaps")

        # توصيات محددة للفئات
        for category, data in results["categories"].items():
            score = data.get("score", 0)

            if category == "code" and score < 70:
                recommendations.append(
                    "Implement code structure according to technical specifications"
                )
                recommendations.append("Set up automated testing pipeline")

            elif category == "documentation" and score < 70:
                recommendations.append("Create comprehensive API documentation")
                recommendations.append("Document system architecture and deployment")

            elif category == "security" and score < 70:
                recommendations.append(
                    "Implement security best practices from compliance studies"
                )
                recommendations.append("Set up automated security scanning")

            elif category == "studies" and score < 70:
                recommendations.append(
                    "Ensure all master study files are present and up-to-date"
                )
                recommendations.append("Review studies compliance regularly")

        return recommendations

    def _save_results(self, results: Dict[str, Any]):
        """حفظ نتائج الفحص"""
        results_file = (
            self.logs_path
            / f"governance_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to: {results_file}")

    def generate_daily_report(self) -> Dict[str, Any]:
        """توليد التقرير اليومي"""
        logger.info("Generating daily governance report...")

        # تشغيل فحص الامتثال
        compliance_results = self.run_compliance_check()

        # إضافة معلومات إضافية للتقرير اليومي
        daily_report = {
            "date": datetime.now().date(),
            "compliance_results": compliance_results,
            "project_status": self._get_project_status(),
            "team_metrics": self._get_team_metrics(),
            "risk_assessment": self._assess_risks(),
            "next_steps": self._generate_next_steps(compliance_results),
        }

        # حفظ التقرير اليومي
        report_file = (
            self.logs_path / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(daily_report, f, indent=2, default=str)

        logger.info(f"Daily report generated: {report_file}")

        return daily_report

    def _get_project_status(self) -> Dict[str, Any]:
        """الحصول على حالة المشروع"""
        # فحص وجود الكود الأساسي
        has_backend = (self.project_root / "src" / "backend").exists()
        has_frontend = (self.project_root / "src" / "frontend").exists()
        has_tests = (self.project_root / "tests").exists()
        has_docs = (self.project_root / "docs").exists()

        return {
            "code_status": "DEVELOPMENT" if has_backend else "NOT_STARTED",
            "frontend_status": "READY" if has_frontend else "NOT_STARTED",
            "testing_status": "SETUP" if has_tests else "NOT_STARTED",
            "documentation_status": "BASIC" if has_docs else "NOT_STARTED",
            "overall_progress": sum([has_backend, has_frontend, has_tests, has_docs])
            / 4
            * 100,
        }

    def _get_team_metrics(self) -> Dict[str, Any]:
        """مقاييس الفريق (محاكاة - يمكن ربطها بأدوات إدارة المشاريع)"""
        return {
            "active_developers": 0,  # يمكن ربطها بـ Git metrics
            "open_tasks": 0,  # يمكن ربطها بـ Jira/Trello
            "completed_tasks": 0,  # يمكن ربطها بـ Jira/Trello
            "code_reviews_pending": 0,  # يمكن ربطها بـ GitHub/GitLab
        }

    def _assess_risks(self) -> List[Dict[str, Any]]:
        """تقييم المخاطر"""
        risks = []

        # مخاطر بناءً على نتائج الفحص
        if not (self.project_root / "src" / "backend").exists():
            risks.append(
                {
                    "level": "HIGH",
                    "category": "TECHNICAL",
                    "description": "Backend development not started",
                    "impact": "Project delay",
                    "mitigation": "Start backend development immediately",
                }
            )

        if not (self.project_root / "tests").exists():
            risks.append(
                {
                    "level": "MEDIUM",
                    "category": "QUALITY",
                    "description": "Testing infrastructure not setup",
                    "impact": "Quality issues in production",
                    "mitigation": "Setup testing framework and CI/CD",
                }
            )

        return risks

    def _generate_next_steps(self, compliance_results: Dict[str, Any]) -> List[str]:
        """توليد الخطوات التالية"""
        next_steps = []

        score = compliance_results.get("overall_score", 0)

        if score < 50:
            next_steps.extend(
                [
                    "🚨 CRITICAL: Schedule emergency governance meeting",
                    "🚨 CRITICAL: Pause development until compliance issues are resolved",
                    "🚨 CRITICAL: Conduct comprehensive project audit",
                ]
            )
        elif score < 70:
            next_steps.extend(
                [
                    "⚠️ HIGH: Address critical compliance gaps immediately",
                    "⚠️ HIGH: Review and update project timeline",
                    "⚠️ HIGH: Increase governance monitoring frequency",
                ]
            )
        elif score < 85:
            next_steps.extend(
                [
                    "📋 MEDIUM: Fix remaining compliance issues",
                    "📋 MEDIUM: Improve documentation coverage",
                    "📋 MEDIUM: Enhance security measures",
                ]
            )
        else:
            next_steps.extend(
                [
                    "✅ GOOD: Continue development with regular monitoring",
                    "✅ GOOD: Focus on optimization and performance",
                    "✅ GOOD: Prepare for next development phase",
                ]
            )

        return next_steps


def main():
    """الدالة الرئيسية"""
    monitor = GovernanceMonitor()

    # تشغيل فحص الامتثال
    results = monitor.run_compliance_check()

    # طباعة النتائج
    print(f"\n{'='*60}")
    print("GOVERNANCE COMPLIANCE CHECK RESULTS")
    print(f"{'='*60}")
    print(f"Overall Score: {results['overall_score']:.1f}%")
    print(f"Timestamp: {results['timestamp']}")
    print()

    print("Category Scores:")
    for category, data in results["categories"].items():
        score = data.get("score", 0)
        status = data.get("status", "UNKNOWN")
        print(f"  {category.title()}: {score:.1f}% ({status})")

    print()
    print("Alerts:")
    for alert in results["alerts"]:
        print(f"  {alert['level']}: {alert['message']}")

    print()
    print("Recommendations:")
    for rec in results["recommendations"]:
        print(f"  • {rec}")

    print(f"\n{'='*60}")

    # توليد التقرير اليومي إذا كان مطلوباً
    if len(sys.argv) > 1 and sys.argv[1] == "--daily":
        daily_report = monitor.generate_daily_report()
        print(f"Daily report generated: {daily_report['date']}")


if __name__ == "__main__":
    main()
