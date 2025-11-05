# @Study:ST-016 @Study:ST-017 @Study:ST-018
"""
اختبارات نظام العمليات الأمنية - Security Operations Tests
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.devops.security.security_ops import SecurityOps


class TestSecurityOps:
    """اختبارات فئة SecurityOps"""

    def setup_method(self):
        """إعداد البيئة لكل اختبار"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir()

        # إنشاء هيكل المشروع
        (self.project_root / "src").mkdir()
        (self.project_root / "tools" / "security").mkdir(parents=True)
        (self.project_root / "scripts" / "devops" / "security").mkdir(parents=True)

    def teardown_method(self):
        """تنظيف البيئة بعد كل اختبار"""
        shutil.rmtree(self.temp_dir)

    @patch("scripts.devops.security.security_ops.Path")
    def test_security_audit_basic_structure(self, mock_path):
        """اختبار هيكل التقرير الأمني الأساسي"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        ops = SecurityOps()
        result = ops.security_audit()

        required_keys = [
            "timestamp",
            "vulnerabilities",
            "compliance_issues",
            "recommendations",
            "score",
        ]
        for key in required_keys:
            assert key in result

        assert isinstance(result["score"], int)
        assert 0 <= result["score"] <= 100

    @patch("scripts.devops.security.security_ops.subprocess.run")
    @patch("scripts.devops.security.security_ops.Path")
    def test_check_dependencies_with_vulnerabilities(self, mock_path, mock_subprocess):
        """اختبار فحص التبعيات مع وجود ثغرات"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        # محاكاة إخراج safety
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "vulnerabilities": [
                    {
                        "package": "test-package",
                        "version": "1.0.0",
                        "severity": "high",
                        "description": "Test vulnerability",
                    }
                ]
            }
        )
        mock_subprocess.return_value = mock_result

        ops = SecurityOps()
        vulnerabilities = ops._check_dependencies()

        assert len(vulnerabilities) == 1
        assert vulnerabilities[0]["severity"] == "high"
        assert vulnerabilities[0]["package"] == "test-package"

    @patch("scripts.devops.security.security_ops.Path")
    def test_check_compliance_with_insecure_env(self, mock_path):
        """اختبار فحص الامتثال مع ملف بيئة غير آمن"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        # إنشاء ملف .env غير آمن
        env_file = self.project_root / ".env"
        env_file.write_text("SECRET_KEY=your-super-secret-key-change-in-production\n")

        ops = SecurityOps()
        issues = ops._check_compliance()

        assert len(issues) > 0
        assert any("dangerous" in issue["description"].lower() for issue in issues)

    @patch("scripts.devops.security.security_ops.Path")
    def test_check_compliance_with_secure_file_permissions(self, mock_path):
        """اختبار فحص صلاحيات الملفات الآمنة"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        # إنشاء ملف حساس بصلاحيات غير آمنة
        key_file = self.project_root / "scripts" / "devops" / "keys" / ".master_key"
        key_file.parent.mkdir(parents=True)
        key_file.write_text("test_key")
        key_file.chmod(0o644)  # صلاحيات غير آمنة

        ops = SecurityOps()
        issues = ops._check_compliance()

        assert len(issues) > 0
        assert any("permissions" in issue["description"].lower() for issue in issues)

    @patch("scripts.devops.security.security_ops.subprocess.run")
    @patch("scripts.devops.security.security_ops.Path")
    def test_check_code_security_with_issues(self, mock_path, mock_subprocess):
        """اختبار فحص أمان الكود مع وجود مشاكل"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        # محاكاة إخراج bandit
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "results": [
                    {
                        "filename": "test.py",
                        "line_number": 10,
                        "issue_text": "Test security issue",
                        "issue_severity": "medium",
                        "issue_confidence": "high",
                    }
                ]
            }
        )
        mock_subprocess.return_value = mock_result

        ops = SecurityOps()
        vulnerabilities = ops._check_code_security()

        assert len(vulnerabilities) == 1
        assert vulnerabilities[0]["severity"] == "medium"
        assert vulnerabilities[0]["file"] == "test.py"

    def test_calculate_security_score_perfect(self):
        """اختبار حساب النتيجة الأمنية المثالية"""
        ops = SecurityOps()
        audit_results = {"vulnerabilities": [], "compliance_issues": []}

        score = ops._calculate_security_score(audit_results)
        assert score == 100

    def test_calculate_security_score_with_issues(self):
        """اختبار حساب النتيجة الأمنية مع وجود مشاكل"""
        ops = SecurityOps()
        audit_results = {
            "vulnerabilities": [{"severity": "high"}, {"severity": "medium"}],
            "compliance_issues": [{"severity": "high"}, {"severity": "low"}],
        }

        score = ops._calculate_security_score(audit_results)
        assert score < 100
        assert score >= 0

    def test_generate_recommendations_based_on_score(self):
        """اختبار توليد التوصيات بناءً على النتيجة"""
        ops = SecurityOps()

        # اختبار نتيجة منخفضة
        low_score_audit = {
            "score": 60,
            "vulnerabilities": [{"type": "dependency"}],
            "compliance_issues": [{"description": "permissions on sensitive files"}],
        }

        recommendations = ops._generate_recommendations(low_score_audit)
        assert len(recommendations) > 0
        assert any("critical" in rec.lower() for rec in recommendations)

    @patch("scripts.devops.security.security_ops.Path")
    def test_generate_security_report_creates_file(self, mock_path):
        """اختبار إنشاء ملف التقرير الأمني"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        ops = SecurityOps()
        report_path = ops.generate_security_report()

        assert Path(report_path).exists()

        # التحقق من محتوى التقرير
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = [
            "timestamp",
            "vulnerabilities",
            "compliance_issues",
            "recommendations",
            "score",
        ]
        for key in required_keys:
            assert key in data

    @patch("scripts.devops.security.security_ops.Path")
    def test_monitor_security_status_no_reports(self, mock_path):
        """اختبار مراقبة الحالة الأمنية بدون تقارير سابقة"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        ops = SecurityOps()
        status = ops.monitor_security_status()

        assert status["last_audit"] is None
        assert status["current_score"] == 0
        assert status["status"] == "unknown"


class TestSecurityOpsIntegration:
    """اختبارات التكامل لنظام العمليات الأمنية"""

    @patch("scripts.devops.security.security_ops.Path")
    def test_full_security_workflow(self, mock_path):
        """اختبار سير العمل الأمني الكامل"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            mock_path.return_value.parent.parent.parent.parent = temp_dir

            ops = SecurityOps()

            # إجراء تدقيق أمني
            audit_result = ops.security_audit()
            assert "score" in audit_result

            # توليد تقرير
            report_path = ops.generate_security_report()
            assert Path(report_path).exists()

            # مراقبة الحالة
            status = ops.monitor_security_status()
            assert "status" in status
            assert status["last_audit"] is not None

        finally:
            shutil.rmtree(temp_dir)

    @patch("scripts.devops.security.security_ops.subprocess.run")
    @patch("scripts.devops.security.security_ops.Path")
    def test_dependency_check_integration(self, mock_path, mock_subprocess):
        """اختبار تكامل فحص التبعيات"""
        mock_path.return_value.parent.parent.parent.parent = self.project_root

        # محاكاة فشل أداة safety
        mock_subprocess.side_effect = FileNotFoundError()

        ops = SecurityOps()
        vulnerabilities = ops._check_dependencies()

        # يجب أن يعيد تقريراً عن فشل الأداة
        assert len(vulnerabilities) == 1
        assert "Failed to check dependencies" in vulnerabilities[0]["description"]
