#!/usr/bin/env python3
# @Study:ST-013 @Study:ST-019
"""
نظام العمليات الأمنية - Security Operations System
يوفر أدوات أمنية متقدمة للعمليات اليومية
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import requests


class SecurityOps:
    """نظام العمليات الأمنية"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.security_dir = self.project_root / "tools" / "security"
        self.reports_dir = self.security_dir / "reports"
        self.security_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def security_audit(self) -> Dict[str, Any]:
        """تدقيق أمني شامل"""
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "compliance_issues": [],
            "recommendations": [],
            "score": 0,
        }

        # فحص التبعيات الأمنية
        audit_results["vulnerabilities"].extend(self._check_dependencies())

        # فحص الامتثال الأمني
        audit_results["compliance_issues"].extend(self._check_compliance())

        # فحص التكوين الأمني
        audit_results["compliance_issues"].extend(self._check_configuration())

        # فحص الكود الأمني
        audit_results["vulnerabilities"].extend(self._check_code_security())

        # حساب النتيجة
        audit_results["score"] = self._calculate_security_score(audit_results)

        # توليد التوصيات
        audit_results["recommendations"] = self._generate_recommendations(audit_results)

        return audit_results

    def _check_dependencies(self) -> List[Dict[str, Any]]:
        """فحص التبعيات الأمنية"""
        vulnerabilities = []

        try:
            # تشغيل safety للتحقق من الثغرات
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                for vuln in data.get("vulnerabilities", []):
                    vulnerabilities.append(
                        {
                            "type": "dependency",
                            "severity": vuln.get("severity", "unknown"),
                            "package": vuln.get("package", ""),
                            "version": vuln.get("version", ""),
                            "description": vuln.get("description", ""),
                            "fix": vuln.get("fix", ""),
                        }
                    )
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            vulnerabilities.append(
                {
                    "type": "dependency",
                    "severity": "error",
                    "description": "Failed to check dependencies - safety not installed or failed",
                }
            )

        return vulnerabilities

    def _check_compliance(self) -> List[Dict[str, Any]]:
        """فحص الامتثال الأمني"""
        issues = []

        # التحقق من وجود مفاتيح أمنية
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                content = f.read()

            # فحص القيم الافتراضية الخطرة
            dangerous_patterns = [
                r"SECRET_KEY=.*your-.*key",
                r"PASSWORD=.*password",
                r"API_KEY=.*your-.*key",
            ]

            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(
                        {
                            "type": "compliance",
                            "severity": "high",
                            "description": f"Dangerous default value found in .env: {pattern}",
                        }
                    )

        # التحقق من صلاحيات الملفات الحساسة
        sensitive_files = [
            ".env",
            "scripts/devops/keys/.master_key",
            "scripts/devops/keys/.secure_store.enc",
        ]

        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                mode = oct(stat.st_mode)[-3:]

                # يجب أن تكون صلاحيات الملفات الحساسة 600
                if mode != "600":
                    issues.append(
                        {
                            "type": "compliance",
                            "severity": "medium",
                            "description": f"Insecure file permissions on {file_path}: {mode} (should be 600)",
                        }
                    )

        return issues

    def _check_configuration(self) -> List[Dict[str, Any]]:
        """فحص التكوين الأمني"""
        issues = []

        # التحقق من إعدادات Docker
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            with open(dockerfile, "r") as f:
                content = f.read()

            # فحص استخدام مستخدم root
            if "USER root" in content or not re.search(r"USER \w+", content):
                issues.append(
                    {
                        "type": "configuration",
                        "severity": "medium",
                        "description": "Docker container may be running as root - consider using non-root user",
                    }
                )

        # التحقق من إعدادات CI/CD
        workflow_file = self.project_root / ".github" / "workflows" / "governance.yml"
        if workflow_file.exists():
            with open(workflow_file, "r") as f:
                content = f.read()

            # التحقق من وجود خطوات أمنية
            security_steps = ["bandit", "safety", "audit"]
            found_security = any(step in content.lower() for step in security_steps)

            if not found_security:
                issues.append(
                    {
                        "type": "configuration",
                        "severity": "low",
                        "description": "CI/CD pipeline missing security scanning steps",
                    }
                )

        return issues

    def _check_code_security(self) -> List[Dict[str, Any]]:
        """فحص أمان الكود"""
        vulnerabilities = []

        try:
            # تشغيل bandit للتحقق من أمان الكود
            result = subprocess.run(
                ["bandit", "-r", "src", "-f", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                for issue in data.get("results", []):
                    vulnerabilities.append(
                        {
                            "type": "code",
                            "severity": issue.get("issue_severity", "unknown"),
                            "file": issue.get("filename", ""),
                            "line": issue.get("line_number", 0),
                            "description": issue.get("issue_text", ""),
                            "confidence": issue.get("issue_confidence", "unknown"),
                        }
                    )
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            vulnerabilities.append(
                {
                    "type": "code",
                    "severity": "error",
                    "description": "Failed to check code security - bandit not installed or failed",
                }
            )

        return vulnerabilities

    def _calculate_security_score(self, audit_results: Dict[str, Any]) -> int:
        """حساب نتيجة الأمان"""
        base_score = 100

        # خصم النقاط لكل ثغرة
        for vuln in audit_results["vulnerabilities"]:
            severity = vuln.get("severity", "low")
            if severity == "high":
                base_score -= 20
            elif severity == "medium":
                base_score -= 10
            elif severity == "low":
                base_score -= 5

        # خصم النقاط لمشاكل الامتثال
        for issue in audit_results["compliance_issues"]:
            severity = issue.get("severity", "low")
            if severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 8
            elif severity == "low":
                base_score -= 3

        return max(0, min(100, base_score))

    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """توليد التوصيات الأمنية"""
        recommendations = []

        if audit_results["score"] < 70:
            recommendations.append("🔴 CRITICAL: Implement immediate security fixes")
        elif audit_results["score"] < 85:
            recommendations.append(
                "🟡 HIGH PRIORITY: Address security vulnerabilities promptly"
            )

        # توصيات محددة
        if any(v["type"] == "dependency" for v in audit_results["vulnerabilities"]):
            recommendations.append(
                "Update vulnerable dependencies using 'poetry update'"
            )

        if any(
            "permissions" in issue["description"].lower()
            for issue in audit_results["compliance_issues"]
        ):
            recommendations.append("Fix file permissions: chmod 600 on sensitive files")

        if any(
            "default" in issue["description"].lower()
            for issue in audit_results["compliance_issues"]
        ):
            recommendations.append(
                "Replace default secrets with secure generated values"
            )

        if not recommendations:
            recommendations.append("✅ Security posture is good - continue monitoring")

        return recommendations

    def generate_security_report(self) -> str:
        """توليد تقرير الأمان"""
        audit_results = self.security_audit()

        report_path = (
            self.reports_dir
            / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False)

        return str(report_path)

    def monitor_security_status(self) -> Dict[str, Any]:
        """مراقبة حالة الأمان"""
        status = {
            "last_audit": None,
            "current_score": 0,
            "critical_issues": 0,
            "status": "unknown",
        }

        # البحث عن آخر تقرير
        if self.reports_dir.exists():
            reports = list(self.reports_dir.glob("security_audit_*.json"))
            if reports:
                latest_report = max(reports, key=lambda x: x.stat().st_mtime)
                status["last_audit"] = latest_report.stat().st_mtime

                with open(latest_report, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    status["current_score"] = data.get("score", 0)
                    status["critical_issues"] = len(
                        [
                            v
                            for v in data.get("vulnerabilities", [])
                            if v.get("severity") in ["high", "critical"]
                        ]
                    )

        # تحديد الحالة
        if status["current_score"] >= 90:
            status["status"] = "excellent"
        elif status["current_score"] >= 75:
            status["status"] = "good"
        elif status["current_score"] >= 60:
            status["status"] = "fair"
        else:
            status["status"] = "critical"

        return status


def main():
    """الواجهة الرئيسية"""
    import argparse

    parser = argparse.ArgumentParser(description="Modamoda Security Operations")
    parser.add_argument("action", choices=["audit", "report", "monitor", "check"])

    args = parser.parse_args()
    ops = SecurityOps()

    if args.action == "audit":
        print("🔍 Running security audit...")
        results = ops.security_audit()
        print(f"📊 Security Score: {results['score']}/100")
        print(f"🚨 Vulnerabilities: {len(results['vulnerabilities'])}")
        print(f"⚠️  Compliance Issues: {len(results['compliance_issues'])}")
        print("\n📋 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")

    elif args.action == "report":
        print("📄 Generating security report...")
        report_path = ops.generate_security_report()
        print(f"✅ Report saved to: {report_path}")

    elif args.action == "monitor":
        print("📊 Security Status Monitor:")
        status = ops.monitor_security_status()
        print(f"  Score: {status['current_score']}/100")
        print(f"  Status: {status['status'].upper()}")
        print(f"  Critical Issues: {status['critical_issues']}")
        if status["last_audit"]:
            print(f"  Last Audit: {datetime.fromtimestamp(status['last_audit'])}")

    elif args.action == "check":
        print("🔍 Quick security check...")
        status = ops.monitor_security_status()
        if status["status"] in ["excellent", "good"]:
            print("✅ Security status is acceptable")
            exit(0)
        else:
            print("❌ Security issues detected - run full audit")
            exit(1)


if __name__ == "__main__":
    main()
