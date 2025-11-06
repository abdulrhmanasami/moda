#!/bin/bash

# Script لتنظيف الملفات المكررة والملفات غير الضرورية
# Modamoda Invisible Mannequin - تنظيف المشروع

set -e  # إيقاف التنفيذ عند أي خطأ

echo "🧹 بدء عملية تنظيف الملفات المكررة والقديمة..."
echo "========================================================"

# إنشاء مجلد الأرشيف
mkdir -p archive/old_files/$(date +%Y%m%d)
ARCHIVE_DIR="archive/old_files/$(date +%Y%m%d)"

echo "📦 إنشاء مجلد الأرشيف: $ARCHIVE_DIR"

# 1. أرشفة وحذف ملفات تغطية الاختبارات
if [ -d "htmlcov" ]; then
    echo "🗂️  نقل مجلد htmlcov للأرشيف..."
    mv htmlcov/ "$ARCHIVE_DIR/"
fi

# 2. أرشفة وحذف ملفات التغطية
for file in coverage_report.txt coverage.xml; do
    if [ -f "$file" ]; then
        echo "📄 نقل $file للأرشيف..."
        mv "$file" "$ARCHIVE_DIR/"
    fi
done

# 3. أرشفة وحذف الإصدارات القديمة
if [ -d "release/v1.0.0-RC3" ]; then
    echo "📦 نقل مجلد الإصدار القديم للأرشيف..."
    mv release/ "$ARCHIVE_DIR/"
fi

# 4. أرشفة وحذف ملفات PDF المكررة
if [ -d "studies" ]; then
    echo "📑 نقل ملفات PDF المكررة للأرشيف..."
    find studies/ -name "*.pdf" -type f -exec mv {} "$ARCHIVE_DIR/" \;
fi

# 5. أرشفة وحذف الملف غير المتعلق
if [ -f "governance/legal/Cursor_Governance_Executive_Ticket.pdf" ]; then
    echo "📋 نقل ملف PDF غير المتعلق للأرشيف..."
    mv "governance/legal/Cursor_Governance_Executive_Ticket.pdf" "$ARCHIVE_DIR/"
    # حذف المجلد إذا كان فارغاً
    rmdir governance/legal/ 2>/dev/null || true
fi

# 6. دمج ملفات الحوكمة المكررة (حذف النسخ البسيطة)
if [ -f "tools/compliance/compliance_checker.py" ]; then
    echo "🔗 إنشاء رابط رمزي لـ compliance_checker.py..."
    rm tools/compliance/compliance_checker.py
    ln -s ../../../scripts/compliance_checker.py tools/compliance/compliance_checker.py
fi

if [ -f "tools/governance/governance_monitor.py" ]; then
    echo "🔗 إنشاء رابط رمزي لـ governance_monitor.py..."
    rm tools/governance/governance_monitor.py
    ln -s ../../../scripts/governance_monitor.py tools/governance/governance_monitor.py
fi

if [ -f "tools/governance/governance_reporter.py" ]; then
    echo "🔗 إنشاء رابط رمزي لـ governance_reporter.py..."
    rm tools/governance/governance_reporter.py
    ln -s ../../../scripts/governance_reporter.py tools/governance/governance_reporter.py
fi

# تحديث .gitignore
echo "📝 تحديث .gitignore..."
cat >> .gitignore << 'EOF'

# Coverage reports
htmlcov/
coverage_report.txt
coverage.xml
*.cover
*.coverage

# Old releases
release/

# Archived files
archive/
EOF

# إنشاء ملف README للأرشيف
cat > "$ARCHIVE_DIR/README.md" << EOF
# أرشيف الملفات المحذوفة
## تاريخ الأرشيف: $(date)

هذا المجلد يحتوي على الملفات التي تم نقلها أثناء عملية التنظيف.

## الملفات المؤرشفة:
- htmlcov/: تقارير تغطية الاختبارات HTML
- coverage_report.txt: تقرير تغطية نصي
- coverage.xml: تقرير تغطية XML
- release/: الإصدارات القديمة
- *.pdf: ملفات PDF المكررة من مجلد studies
- Cursor_Governance_Executive_Ticket.pdf: ملف غير متعلق

## ملاحظات:
- يمكن حذف هذا المجلد بعد شهر من التأكد من عدم الحاجة للملفات
- جميع الملفات الأساسية محفوظة في ملفات Markdown

تاريخ الأرشيف: $(date)
EOF

echo ""
echo "✅ تم إكمال عملية التنظيف بنجاح!"
echo "========================================================"
echo "📊 ملخص العمليات:"
echo "  • أرشفة $(find "$ARCHIVE_DIR" -type f | wc -l) ملف"
echo "  • إنشاء $(find "$ARCHIVE_DIR" -type d | wc -l) مجلد مؤرشف"
echo "  • إنشاء $(ls tools/governance/*.py tools/compliance/*.py 2>/dev/null | wc -l) رابط رمزي"
echo ""
echo "🔍 للتحقق من سلامة المشروع:"
echo "  python scripts/compliance_checker.py"
echo "  python scripts/governance_monitor.py"
echo ""
echo "📁 الملفات المؤرشفة محفوظة في: $ARCHIVE_DIR"
echo "⚠️  يمكن حذف مجلد archive/ بعد شهر من التأكد من عدم الحاجة"
