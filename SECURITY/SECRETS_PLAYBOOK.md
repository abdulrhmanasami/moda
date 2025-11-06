# Secrets Incident Playbook

## 1) إيقاف النزف (Rotate & Revoke)

- لو السر حقيقي: عطّل/دوّر المفتاح فوراً عند المزود (GitHub Token/AWS/API Key).

- دوّن كل الأماكن اللي عم تُستخدم فيها المفاتيح واستبدلها بالقيم الجديدة عبر Secret Manager.



## 2) فتح تذكرة تتبع

- Issue: `SEC-LEAK-YYYYMMDD-xx` تتضمن: الرابط للكومِت/الملف، نوع السر، أثر التسريب، حالة التدوير.



## 3) تنظيف التاريخ (History Rewrite) *بإدارة موافقات*

> تحضير نافذة صيانة + تجميد الدمج.

- أنشئ ملف استبدال: `tools/security/secret-replacements.txt` يحوي سطر مثل:

  `regex:YOUR_REAL_SECRET_OR_STRICT_REGEX==>REDACTED`

- جرّب محلياً على نسخة منفصلة أولاً.



### باستخدام git-filter-repo (الموصى به)

- ثبّت الأداة: https://github.com/newren/git-filter-repo

- نفّذ:

  ```bash

  git checkout $DEFAULT_BRANCH

  git pull --ff-only

  git filter-repo --replace-text tools/security/secret-replacements.txt --force

  git push --force

```



* كرر على الفروع المتأثرة، ثم فعّل حماية الفرع بعد الانتهاء.



## 4) التحقق



* شغّل gitleaks محلياً وعلى الريموت (PR) للتأكد من زوال التحذيرات.

* راقب Code Scanning + Logs.



## 5) ما بعد الحادثة



* أضف Regex مناسبة لـ `.gitleaks.toml` لتجنّب تكرار نفس النمط (بحذر).

* حدّث وثائق السر (Secret Owner, Rotation Policy, TTL).
