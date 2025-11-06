# @Study:ST-013
# @Study:ST-011
# @Study:ST-007
# @Study:ST-019
#!/usr/bin/env python3
"""
نظام فحص الامتثال التلقائي - Automated Compliance Checker
يضمن الامتثال الكامل مع الدراسات والمعايير الفنية
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ComplianceChecker:
    """
    نظام فحص الامتثال الشامل والتلقائي
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.studies_path = self.project_root / "studies"
        self.src_path = self.project_root / "src"
        self.tests_path = self.project_root / "tests"

        # معايير الامتثال من الدراسات
        self.compliance_rules = {
            "architecture": {
                "required_dirs": ["backend", "frontend", "shared"],
                "backend_framework": "fastapi",
                "frontend_framework": "next",
                "database": "postgresql",
                "cache": "redis",
                "task_queue": "celery",
            },
            "code_quality": {
                "min_test_coverage": 80,
                "max_complexity": 10,
                "line_length_limit": 88,
                "required_docstrings": True,
            },
            "security": {
                "encryption_required": True,
                "auth_required": True,
                "input_validation": True,
                "secure_headers": True,
            },
            "documentation": {
                "api_docs_required": True,
                "architecture_docs": True,
                "deployment_docs": True,
                "readme_updated": True,
            },
        }

    def run_full_compliance_check(self) -> Dict[str, Any]:
        """
        تشغيل فحص امتثال شامل
        """
        print("🔍 بدء فحص الامتثال الشامل...")

        results = {
            "timestamp": datetime.now(),
            "overall_compliance": 0,
            "categories": {},
            "violations": [],
            "recommendations": [],
            "critical_issues": [],
        }

        # فحص امتثال المعمارية
        arch_compliance = self.check_architecture_compliance()
        results["categories"]["architecture"] = arch_compliance

        # فحص امتثال الكود
        code_compliance = self.check_code_compliance()
        results["categories"]["code"] = code_compliance

        # فحص امتثال الأمان
        security_compliance = self.check_security_compliance()
        results["categories"]["security"] = security_compliance

        # فحص امتثال التوثيق
        docs_compliance = self.check_documentation_compliance()
        results["categories"]["documentation"] = docs_compliance

        # فحص امتثال الاختبارات
        test_compliance = self.check_testing_compliance()
        results["categories"]["testing"] = test_compliance

        # حساب الامتثال العام
        results["overall_compliance"] = self.calculate_overall_compliance(
            results["categories"]
        )

        # تحديد المخالفات والتوصيات
        results["violations"] = self.identify_violations(results["categories"])
        results["recommendations"] = self.generate_recommendations(
            results["categories"]
        )
        results["critical_issues"] = self.identify_critical_issues(
            results["categories"]
        )

        # طباعة التقرير
        self.print_compliance_report(results)

        return results

    def check_architecture_compliance(self) -> Dict[str, Any]:
        """فحص امتثال المعمارية مع الدراسات"""
        compliance = {"score": 0, "status": "UNKNOWN", "checks": {}, "issues": []}

        # فحص وجود المجلدات المطلوبة
        required_dirs = self.compliance_rules["architecture"]["required_dirs"]
        existing_dirs = (
            [d.name for d in self.src_path.iterdir() if d.is_dir()]
            if self.src_path.exists()
            else []
        )

        dir_compliance = (
            len(set(required_dirs) & set(existing_dirs)) / len(required_dirs) * 100
        )
        compliance["checks"]["directory_structure"] = {
            "score": dir_compliance,
            "required": required_dirs,
            "existing": existing_dirs,
            "missing": list(set(required_dirs) - set(existing_dirs)),
        }

        # فحص إطار العمل الخلفي
        backend_compliance = self.check_backend_framework()
        compliance["checks"]["backend_framework"] = backend_compliance

        # فحص إطار العمل الأمامي
        frontend_compliance = self.check_frontend_framework()
        compliance["checks"]["frontend_framework"] = frontend_compliance

        # فحص قاعدة البيانات والتخزين المؤقت
        infra_compliance = self.check_infrastructure_setup()
        compliance["checks"]["infrastructure"] = infra_compliance

        # حساب النتيجة الإجمالية
        scores = [check["score"] for check in compliance["checks"].values()]
        compliance["score"] = sum(scores) / len(scores) if scores else 0

        # تحديد الحالة
        if compliance["score"] >= 80:
            compliance["status"] = "COMPLIANT"
        elif compliance["score"] >= 60:
            compliance["status"] = "PARTIALLY_COMPLIANT"
        else:
            compliance["status"] = "NON_COMPLIANT"

        # تحديد المشاكل
        for check_name, check_data in compliance["checks"].items():
            if check_data["score"] < 70:
                compliance["issues"].append(
                    f"Low compliance in {check_name}: {check_data['score']:.1f}%"
                )

        return compliance

    def check_backend_framework(self) -> Dict[str, Any]:
        """فحص إطار العمل الخلفي"""
        backend_path = self.src_path / "backend"
        pyproject_file = self.project_root / "pyproject.toml"

        compliance = {"score": 0, "details": {}}

        if not backend_path.exists():
            compliance["details"]["backend_exists"] = False
            return compliance

        # فحص ملف pyproject.toml
        if pyproject_file.exists():
            with open(pyproject_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "fastapi" in content.lower():
                    compliance["score"] += 50
                    compliance["details"]["fastapi_dependency"] = True
                else:
                    compliance["details"]["fastapi_dependency"] = False

        # فحص وجود ملفات FastAPI
        main_files = list(backend_path.glob("**/main.py")) + list(
            backend_path.glob("**/app.py")
        )
        if main_files:
            compliance["score"] += 30
            compliance["details"]["main_file_exists"] = True
        else:
            compliance["details"]["main_file_exists"] = False

        # فحص وجود ملفات التطبيق الأساسية
        required_files = ["models", "routes", "services", "config"]
        existing_files = []
        for pattern in ["*.py", "**/*.py"]:
            existing_files.extend([f.stem for f in backend_path.glob(pattern)])

        matched_files = len(set(required_files) & set(existing_files))
        file_score = (matched_files / len(required_files)) * 20
        compliance["score"] += file_score
        compliance["details"][
            "code_structure"
        ] = f"{matched_files}/{len(required_files)}"

        return compliance

    def check_frontend_framework(self) -> Dict[str, Any]:
        """فحص إطار العمل الأمامي"""
        frontend_path = self.src_path / "frontend"
        package_file = frontend_path / "package.json"

        compliance = {"score": 0, "details": {}}

        if not frontend_path.exists():
            compliance["details"]["frontend_exists"] = False
            return compliance

        # فحص package.json
        if package_file.exists():
            with open(package_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    dependencies = str(data.get("dependencies", {})).lower()

                    if "next" in dependencies:
                        compliance["score"] += 60
                        compliance["details"]["nextjs_dependency"] = True
                    else:
                        compliance["details"]["nextjs_dependency"] = False

                    if "react" in dependencies:
                        compliance["score"] += 20
                        compliance["details"]["react_dependency"] = True
                    else:
                        compliance["details"]["react_dependency"] = False

                except json.JSONDecodeError:
                    compliance["details"]["package_json_valid"] = False
        else:
            compliance["details"]["package_json_exists"] = False

        # فحص هيكل Next.js
        nextjs_files = ["pages", "components", "public", "styles"]
        existing_nextjs = [d for d in nextjs_files if (frontend_path / d).exists()]
        structure_score = (len(existing_nextjs) / len(nextjs_files)) * 20
        compliance["score"] += structure_score
        compliance["details"][
            "nextjs_structure"
        ] = f"{len(existing_nextjs)}/{len(nextjs_files)}"

        return compliance

    def check_infrastructure_setup(self) -> Dict[str, Any]:
        """فحص إعداد البنية التحتية"""
        compliance = {"score": 0, "details": {}}

        # فحص Docker
        dockerfile = self.project_root / "Dockerfile"
        docker_compose = self.project_root / "docker-compose.yml"

        if dockerfile.exists():
            compliance["score"] += 25
            compliance["details"]["dockerfile_exists"] = True
        else:
            compliance["details"]["dockerfile_exists"] = False

        if docker_compose.exists():
            compliance["score"] += 25
            compliance["details"]["docker_compose_exists"] = True
        else:
            compliance["details"]["docker_compose_exists"] = False

        # فحص التكوين
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject, "r", encoding="utf-8") as f:
                content = f.read()
                if "postgresql" in content.lower():
                    compliance["score"] += 20
                    compliance["details"]["postgres_config"] = True
                if "redis" in content.lower():
                    compliance["score"] += 15
                    compliance["details"]["redis_config"] = True
                if "celery" in content.lower():
                    compliance["score"] += 15
                    compliance["details"]["celery_config"] = True

        return compliance

    def check_code_compliance(self) -> Dict[str, Any]:
        """فحص امتثال الكود للمعايير"""
        compliance = {"score": 0, "status": "UNKNOWN", "checks": {}, "issues": []}

        if not self.src_path.exists():
            compliance["issues"].append("Source directory does not exist")
            return compliance

        # فحص جودة الكود
        quality_check = self.check_code_quality()
        compliance["checks"]["quality"] = quality_check

        # فحص تغطية الاختبارات
        coverage_check = self.check_test_coverage()
        compliance["checks"]["coverage"] = coverage_check

        # فحص الأمان في الكود
        security_check = self.check_code_security()
        compliance["checks"]["security"] = security_check

        # حساب النتيجة
        scores = [check["score"] for check in compliance["checks"].values()]
        compliance["score"] = sum(scores) / len(scores) if scores else 0

        if compliance["score"] >= 80:
            compliance["status"] = "HIGH_QUALITY"
        elif compliance["score"] >= 60:
            compliance["status"] = "ACCEPTABLE"
        else:
            compliance["status"] = "NEEDS_IMPROVEMENT"

        return compliance

    def check_code_quality(self) -> Dict[str, Any]:
        """فحص جودة الكود"""
        quality = {"score": 0, "metrics": {}}

        # فحص ملفات Python
        python_files = list(self.src_path.glob("**/*.py"))
        if not python_files:
            return quality

        total_lines = 0
        long_lines = 0
        documented_functions = 0
        total_functions = 0

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                # فحص طول الأسطر
                for line in lines:
                    if (
                        len(line)
                        > self.compliance_rules["code_quality"]["line_length_limit"]
                    ):
                        long_lines += 1
                total_lines += len(lines)

                # فحص التوثيق (بسيط)
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        if ast.get_docstring(node):
                            documented_functions += 1

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        # حساب المقاييس
        if total_lines > 0:
            line_compliance = max(0, 100 - (long_lines / total_lines * 100))
            quality["metrics"]["line_length"] = f"{line_compliance:.1f}%"
            quality["score"] += line_compliance * 0.4

        if total_functions > 0:
            doc_compliance = (documented_functions / total_functions) * 100
            quality["metrics"]["documentation"] = f"{doc_compliance:.1f}%"
            quality["score"] += doc_compliance * 0.6

        return quality

    def check_test_coverage(self) -> Dict[str, Any]:
        """فحص تغطية الاختبارات"""
        coverage = {"score": 0, "details": {}}

        if not self.tests_path.exists():
            coverage["details"]["tests_exist"] = False
            return coverage

        # عد ملفات الاختبار
        test_files = list(self.tests_path.glob("**/*.py"))
        coverage["details"]["test_files_count"] = len(test_files)

        # عد ملفات الكود المصدر
        src_files = list(self.src_path.glob("**/*.py"))
        coverage["details"]["src_files_count"] = len(src_files)

        if src_files:
            coverage_ratio = len(test_files) / len(src_files)
            coverage_score = min(100, coverage_ratio * 100)  # نسبة مئوية
            coverage["score"] = coverage_score
            coverage["details"][
                "coverage_ratio"
            ] = f"{len(test_files)}/{len(src_files)}"

        return coverage

    def check_code_security(self) -> Dict[str, Any]:
        """فحص الأمان في الكود"""
        security = {"score": 0, "issues": [], "good_practices": []}

        python_files = list(self.src_path.glob("**/*.py"))

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # فحص الممارسات السيئة
                if "eval(" in content:
                    security["issues"].append(f"eval() found in {file_path}")
                if "exec(" in content:
                    security["issues"].append(f"exec() found in {file_path}")
                if "input(" in content and "validate" not in content:
                    security["issues"].append(f"Unvalidated input() in {file_path}")

                # فحص الممارسات الجيدة
                if "bcrypt" in content or "cryptography" in content:
                    security["good_practices"].append("Encryption library used")
                if "jwt" in content or "oauth" in content:
                    security["good_practices"].append("Authentication library used")

            except Exception as e:
                print(f"Error checking security in {file_path}: {e}")

        # حساب النتيجة
        if not security["issues"]:
            security["score"] = 100
        else:
            security["score"] = max(0, 100 - len(security["issues"]) * 20)

        return security

    def check_security_compliance(self) -> Dict[str, Any]:
        """فحص امتثال الأمان"""
        compliance = {"score": 0, "status": "UNKNOWN", "checks": {}, "issues": []}

        # فحص وجود ملفات الأمان
        security_files = [".gitignore", "pyproject.toml"]
        security_score = sum(
            1 for f in security_files if (self.project_root / f).exists()
        )
        security_score = (security_score / len(security_files)) * 100
        compliance["checks"]["security_files"] = {"score": security_score}

        # فحص إعدادات الأمان في التكوين
        config_security = 0
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            with open(pyproject_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "cryptography" in content or "bcrypt" in content:
                    config_security = 100
        compliance["checks"]["security_config"] = {"score": config_security}

        # فحص وجود ملفات أمان إضافية
        additional_security = 0
        if pyproject_file.exists():
            with open(pyproject_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "bandit" in content:  # security scanner
                    additional_security += 25
                if "safety" in content:  # vulnerability scanner
                    additional_security += 25
                if "sentry" in content:  # error monitoring
                    additional_security += 25
        compliance["checks"]["additional_security"] = {"score": additional_security}

        # حساب النتيجة الإجمالية
        scores = [check["score"] for check in compliance["checks"].values()]
        compliance["score"] = sum(scores) / len(scores) if scores else 0

        if compliance["score"] >= 80:
            compliance["status"] = "SECURE"
        elif compliance["score"] >= 60:
            compliance["status"] = "MODERATELY_SECURE"
        else:
            compliance["status"] = "NEEDS_SECURITY_REVIEW"

        return compliance

    def check_documentation_compliance(self) -> Dict[str, Any]:
        """فحص امتثال التوثيق"""
        docs_path = self.project_root / "docs"

        compliance = {"score": 0, "status": "UNKNOWN", "checks": {}, "issues": []}

        if not docs_path.exists():
            compliance["issues"].append("Documentation directory does not exist")
            compliance["status"] = "MISSING"
            return compliance

        # فحص مجلدات التوثيق المطلوبة
        required_docs = ["api", "architecture", "deployment"]
        existing_docs = [d.name for d in docs_path.iterdir() if d.is_dir()]

        doc_coverage = len(set(required_docs) & set(existing_docs))
        doc_score = (doc_coverage / len(required_docs)) * 100
        compliance["checks"]["doc_structure"] = {
            "score": doc_score,
            "required": required_docs,
            "existing": existing_docs,
        }

        # فحص README
        readme_file = self.project_root / "README.md"
        if readme_file.exists():
            compliance["checks"]["readme"] = {"score": 100, "exists": True}
        else:
            compliance["checks"]["readme"] = {"score": 0, "exists": False}
            compliance["issues"].append("README.md missing")

        # حساب النتيجة الإجمالية
        scores = [check["score"] for check in compliance["checks"].values()]
        compliance["score"] = sum(scores) / len(scores) if scores else 0

        if compliance["score"] >= 80:
            compliance["status"] = "WELL_DOCUMENTED"
        elif compliance["score"] >= 50:
            compliance["status"] = "PARTIALLY_DOCUMENTED"
        else:
            compliance["status"] = "UNDER_DOCUMENTED"

        return compliance

    def check_testing_compliance(self) -> Dict[str, Any]:
        """فحص امتثال نظام الاختبارات"""
        compliance = {"score": 0, "status": "UNKNOWN", "checks": {}, "issues": []}

        # فحص وجود مجلد الاختبارات
        if not self.tests_path.exists():
            compliance["issues"].append("Tests directory does not exist")
            compliance["status"] = "NO_TESTS"
            return compliance

        # عد ملفات الاختبار
        test_files = list(self.tests_path.glob("**/*.py"))
        compliance["checks"]["test_files"] = {
            "count": len(test_files),
            "score": min(100, len(test_files) * 10),  # 10 نقاط لكل ملف اختبار
        }

        # فحص وجود ملفات التكوين
        config_files = ["conftest.py", "pytest.ini", "__init__.py"]
        existing_config = sum(1 for f in config_files if (self.tests_path / f).exists())
        config_score = (existing_config / len(config_files)) * 100
        compliance["checks"]["test_config"] = {"score": config_score}

        # حساب النتيجة
        scores = [check["score"] for check in compliance["checks"].values()]
        compliance["score"] = sum(scores) / len(scores) if scores else 0

        if compliance["score"] >= 80:
            compliance["status"] = "WELL_TESTED"
        elif compliance["score"] >= 50:
            compliance["status"] = "ADEQUATELY_TESTED"
        else:
            compliance["status"] = "INSUFFICIENT_TESTING"

        return compliance

    def calculate_overall_compliance(self, categories: Dict[str, Dict]) -> float:
        """حساب الامتثال العام"""
        if not categories:
            return 0

        # weights for different categories
        weights = {
            "architecture": 0.25,
            "code": 0.25,
            "security": 0.20,
            "documentation": 0.15,
            "testing": 0.15,
        }

        weighted_score = 0
        total_weight = 0

        for category, data in categories.items():
            if category in weights:
                score = data.get("score", 0)
                weight = weights[category]
                weighted_score += score * weight
                total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0

    def identify_violations(self, categories: Dict[str, Dict]) -> List[str]:
        """تحديد المخالفات"""
        violations = []

        for category, data in categories.items():
            score = data.get("score", 0)
            if score < 60:
                violations.append(
                    f"Critical: {category} compliance is below 60% ({score:.1f}%)"
                )

            # مخالفات محددة للفئات
            if category == "architecture":
                if "issues" in data:
                    violations.extend(
                        [f"Architecture: {issue}" for issue in data["issues"]]
                    )

            elif category == "security":
                if "issues" in data.get("checks", {}).get("security", []):
                    violations.extend(
                        [
                            f"Security: {issue}"
                            for issue in data["checks"]["security"]["issues"]
                        ]
                    )

        return violations

    def generate_recommendations(self, categories: Dict[str, Dict]) -> List[str]:
        """توليد التوصيات"""
        recommendations = []

        for category, data in categories.items():
            score = data.get("score", 0)

            if category == "architecture" and score < 70:
                recommendations.extend(
                    [
                        "Create proper directory structure according to technical specifications",
                        "Implement FastAPI backend with proper project structure",
                        "Set up Next.js frontend with TypeScript",
                        "Configure PostgreSQL, Redis, and Celery as specified",
                    ]
                )

            elif category == "code" and score < 70:
                recommendations.extend(
                    [
                        "Implement automated code quality checks (black, flake8, mypy)",
                        "Set up comprehensive testing framework",
                        "Add proper documentation and docstrings",
                        "Implement security best practices in code",
                    ]
                )

            elif category == "security" and score < 70:
                recommendations.extend(
                    [
                        "Implement proper authentication and authorization",
                        "Add input validation and sanitization",
                        "Configure secure headers and CORS policies",
                        "Set up encryption for sensitive data",
                    ]
                )

            elif category == "documentation" and score < 70:
                recommendations.extend(
                    [
                        "Create comprehensive API documentation",
                        "Document system architecture and design decisions",
                        "Write deployment and operations guides",
                        "Update README with current project status",
                    ]
                )

            elif category == "testing" and score < 70:
                recommendations.extend(
                    [
                        "Set up pytest with proper configuration",
                        "Implement unit tests for all modules",
                        "Add integration and end-to-end tests",
                        "Configure CI/CD with automated testing",
                    ]
                )

        return recommendations

    def identify_critical_issues(self, categories: Dict[str, Dict]) -> List[str]:
        """تحديد المشاكل الحرجة"""
        critical_issues = []

        for category, data in categories.items():
            score = data.get("score", 0)

            if score < 40:
                critical_issues.append(
                    f"🚨 CRITICAL: {category.title()} compliance is critically low ({score:.1f}%)"
                )

            # مشاكل حرجة محددة
            if category == "architecture":
                checks = data.get("checks", {})
                if checks.get("directory_structure", {}).get("score", 0) < 30:
                    critical_issues.append(
                        "🚨 CRITICAL: Project structure does not match technical specifications"
                    )

            if category == "security":
                security_checks = data.get("checks", {}).get("security", {})
                if security_checks.get("score", 0) < 50:
                    critical_issues.append(
                        "🚨 CRITICAL: Security vulnerabilities detected in code"
                    )

        return critical_issues

    def print_compliance_report(self, results: Dict[str, Any]):
        """طباعة تقرير الامتثال"""
        print(f"\n{'='*80}")
        print("📋 تقرير امتثال شامل - COMPREHENSIVE COMPLIANCE REPORT")
        print(f"{'='*80}")
        print(f"📊 الامتثال العام: {results['overall_compliance']:.1f}%")
        print(f"🕒 التاريخ: {results['timestamp']}")
        print()

        print("📈 نتائج الفئات:")
        for category, data in results["categories"].items():
            score = data.get("score", 0)
            status = data.get("status", "UNKNOWN")
            emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"  {emoji} {category.title()}: {score:.1f}% ({status})")

        print()
        print("🚨 المشاكل الحرجة:")
        for issue in results["critical_issues"]:
            print(f"  {issue}")

        print()
        print("⚠️ المخالفات:")
        for violation in results["violations"]:
            print(f"  • {violation}")

        print()
        print("💡 التوصيات:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")

        print(f"\n{'='*80}")

        # رسالة التلخيص
        if results["overall_compliance"] >= 80:
            print("🎉 الامتثال ممتاز! المشروع جاهز للتطوير مع معايير عالية.")
        elif results["overall_compliance"] >= 60:
            print("⚠️ امتثال مقبول. يحتاج إلى تحسينات قبل التطوير الكامل.")
        else:
            print("❌ امتثال منخفض حرج! يتطلب مراجعة شاملة فورية.")


def main():
    """الدالة الرئيسية"""
    checker = ComplianceChecker()
    results = checker.run_full_compliance_check()

    # حفظ النتائج في ملف
    output_file = (
        Path(__file__).parent.parent
        / "logs"
        / f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n📄 تم حفظ التقرير في: {output_file}")


if __name__ == "__main__":
    main()
