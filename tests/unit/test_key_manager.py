# @Study:ST-016 @Study:ST-017 @Study:ST-018
"""
اختبارات مدير المفاتيح - Key Manager Tests
"""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from scripts.devops.keys.key_manager import KeyManager


class TestKeyManager:
    """اختبارات فئة KeyManager"""

    def setup_method(self):
        """إعداد البيئة لكل اختبار"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.keys_dir = self.temp_dir / "keys"
        self.keys_dir.mkdir()

    def teardown_method(self):
        """تنظيف البيئة بعد كل اختبار"""
        shutil.rmtree(self.temp_dir)

    def test_initialization_creates_master_key(self):
        """اختبار إنشاء المفتاح الرئيسي عند التهيئة"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            master_key_file = self.keys_dir / ".master_key"
            assert master_key_file.exists()
            assert master_key_file.stat().st_mode & 0o777 == 0o600  # صلاحيات مقيدة

    def test_generate_secure_key_length(self):
        """اختبار طول المفتاح المنشأ"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            key = km.generate_secure_key(16)
            assert len(key) == 32  # hex encoding doubles the length
            assert key.isalnum()

    def test_set_and_get_secret(self):
        """اختبار حفظ واسترجاع السر"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            # حفظ سر
            success = km.set_secret("test_key", "test_value", "production")
            assert success

            # استرجاع السر
            value = km.get_secret("test_key", "production")
            assert value == "test_value"

    def test_get_nonexistent_secret(self):
        """اختبار استرجاع سر غير موجود"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            value = km.get_secret("nonexistent_key")
            assert value is None

    def test_rotate_master_key(self):
        """اختبار تدوير المفتاح الرئيسي"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            # حفظ سر
            km.set_secret("test_key", "test_value")

            # تدوير المفتاح
            success = km.rotate_master_key()
            assert success

            # التأكد من إمكانية استرجاع السر بعد التدوير
            value = km.get_secret("test_key")
            assert value == "test_value"

    def test_validate_secure_environment(self):
        """اختبار التحقق من ملف البيئة الآمن"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            # إنشاء ملف بيئة آمن
            env_file = self.temp_dir / ".env"
            env_file.write_text(
                """\
SECRET_KEY=secure_random_key_12345
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET_KEY=another_secure_key_67890
"""
            )

            result = km.validate_environment(env_file)
            assert result["valid"] is True
            assert len(result["issues"]) == 0

    def test_validate_insecure_environment(self):
        """اختبار التحقق من ملف البيئة غير الآمن"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            # إنشاء ملف بيئة غير آمن
            env_file = self.temp_dir / ".env"
            env_file.write_text(
                """\
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=postgresql://user:pass@localhost/db
"""
            )

            result = km.validate_environment(env_file)
            assert result["valid"] is False
            assert len(result["issues"]) > 0
            assert any("dangerous" in issue.lower() for issue in result["issues"])

    def test_list_secrets_masks_values(self):
        """اختبار سرد الأسرار مع إخفاء القيم"""
        with patch("scripts.devops.keys.key_manager.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.parent = self.temp_dir

            km = KeyManager()

            # حفظ عدة أسرار
            km.set_secret("key1", "value1", "prod")
            km.set_secret("key2", "value2", "prod")

            secrets = km.list_secrets("prod")
            assert len(secrets) == 2
            assert all(value == "***" for value in secrets.values())


class TestKeyManagerIntegration:
    """اختبارات التكامل لمدير المفاتيح"""

    def test_persistence_across_instances(self):
        """اختبار استمرارية البيانات عبر النسخ"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            with patch("scripts.devops.keys.key_manager.Path") as mock_path:
                mock_path.return_value.parent.parent.parent.parent = temp_dir

                # إنشاء نسخة أولى وحفظ سر
                km1 = KeyManager()
                km1.set_secret("persistent_key", "persistent_value")

                # إنشاء نسخة ثانية واسترجاع السر
                km2 = KeyManager()
                value = km2.get_secret("persistent_key")

                assert value == "persistent_value"

        finally:
            shutil.rmtree(temp_dir)

    def test_encryption_integrity(self):
        """اختبار سلامة التشفير"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            with patch("scripts.devops.keys.key_manager.Path") as mock_path:
                mock_path.return_value.parent.parent.parent.parent = temp_dir

                km = KeyManager()

                # حفظ سر
                km.set_secret("integrity_test", "test_data_123")

                # قراءة ملف المتجر المشفر مباشرة
                store_file = temp_dir / "keys" / ".secure_store.enc"
                assert store_file.exists()

                with open(store_file, "rb") as f:
                    encrypted_data = f.read()

                # التأكد من أن البيانات مشفرة (ليست نصاً عادياً)
                assert b"test_data_123" not in encrypted_data
                assert len(encrypted_data) > len("test_data_123")

        finally:
            shutil.rmtree(temp_dir)
