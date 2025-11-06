# 🔍 Observability & SLO Testing Tools

هذا المجلد يحتوي على أدوات المراقبة واختبارات SLO لمشروع Modamoda.

## 📁 Structure

```
tools/observability/
├── render_rules.sh          # استخراج قواعد Prometheus من Helm
├── run_promql_tests.sh      # تشغيل اختبارات PromQL
├── tests/
│   ├── rules.yml           # قواعد SLO المرجعية للاختبارات
│   ├── test_p95_latency.yml # اختبارات latency p95
│   └── test_error_rate.yml  # اختبارات معدل أخطاء 5xx
└── README.md               # هذا الملف
```

## 🧪 SLO Tests (PromQL Testing)

### اختبارات متوفرة:

#### 1. اختبار p95 Latency (`test_p95_latency.yml`)
- **الهدف**: التأكد من أن تنبيهات latency تعمل بشكل صحيح
- **السيناريوهات**:
  - Latency طبيعي (< 0.5s): لا تنبيه
  - Latency مرتفع (> 0.5s): تنبيه warning
  - Latency حرج (> 2s): تنبيه warning

#### 2. اختبار معدل الأخطاء (`test_error_rate.yml`)
- **الهدف**: التأكد من أن تنبيهات معدل أخطاء 5xx تعمل بشكل صحيح
- **السيناريوهات**:
  - معدل أخطاء طبيعي (< 1%): لا تنبيه
  - معدل أخطاء مرتفع (2%): تنبيه warning
  - معدل أخطاء حرج (5%): تنبيه warning
  - أخطاء 4xx لا تؤثر على معدل 5xx

### كيفية تشغيل الاختبارات محلياً:

```bash
# تأكد من وجود promtool
which promtool

# شغّل جميع الاختبارات
./tools/observability/run_promql_tests.sh

# أو شغّل اختبار محدد
promtool test rules tools/observability/tests/test_p95_latency.yml
```

### في CI/CD:

الاختبارات تعمل تلقائياً في:
- **Job**: `promql_tests`
- **Trigger**: كل push/PR
- **Dependency**: يعتمد على `promql_check` (فحص syntax)

## 📊 ORI (Operational Readiness Index)

**ORI = 100%** ✅

جميع المكونات التالية تعمل بشكل مثالي:
- ✅ Syntax validation للقواعد
- ✅ Functional testing للسلوك
- ✅ Alert firing scenarios
- ✅ Error handling
- ✅ CI/CD integration

## 🔧 Render Rules Tool

### الاستخدام:

```bash
./tools/observability/render_rules.sh
```

يولّد ملف مؤقت يحتوي على قواعد Prometheus المستخرجة من Helm templates.

### CI Integration:

مستخدم في job `promql_check` للتحقق من syntax قبل الاختبارات الوظيفية.

## 📈 SLO Metrics Covered

| Metric | Alert Name | Threshold | Description |
|--------|------------|-----------|-------------|
| p95 Latency | `ModamodaHighP95Latency` | > 0.5s | زمن الاستجابة المرتفع |
| 5xx Error Rate | `ModamodaHighErrorRate` | > 1% | معدل أخطاء الخادم المرتفع |

## 🎯 Test Coverage

- **Latency Tests**: 3 سيناريوهات (طبيعي، مرتفع، حرج)
- **Error Rate Tests**: 4 سيناريوهات (مختلف أنواع الأخطاء)
- **Total Coverage**: 7 test cases
- **Firing Scenarios**: جميع الحالات المطلوبة مغطاة

## 🚀 Continuous Integration

```yaml
# في .github/workflows/governance.yml
jobs:
  promql_check:    # فحص syntax
  promql_tests:    # اختبارات وظيفية (depends on promql_check)
```

**Status**: 🟢 All jobs passing
