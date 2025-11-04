<!-- @Study:ST-015 -->
<!-- @Study:ST-013 -->
<!-- @Study:ST-011 -->
<!-- @Study:ST-005 -->
# @Study:ST-019
# المواصفات التقنية الشاملة
## Modamoda Invisible Mannequin Platform

**المؤلف:** Cursor (auto-generated)  
**التاريخ:** 3 نوفمبر 2025  
**الإصدار:** v2.0  
**الحالة:** محدث ومنسق  

---

## نظرة عامة على البنية التقنية

### المكدس التقني الأساسي

#### 1. الواجهة الخلفية (Backend)
```
Python 3.11+
├── FastAPI (إطار العمل الرئيسي)
├── Celery (إدارة المهام غير المتزامنة)
├── Redis (وسيط الرسائل)
├── PostgreSQL (قاعدة البيانات)
└── Docker/Kubernetes (الحاويات والتنسيق)
```

#### 2. الواجهة الأمامية (Frontend)
```
Next.js 14+ (React Framework)
├── Progressive Web App (PWA)
├── TailwindCSS (التصميم)
├── TypeScript (الأمان النوعي)
└── Vercel/Netlify (الاستضافة)
```

#### 3. البنية التحتية (Infrastructure)
```
Amazon Web Services / Google Cloud Platform
├── EC2/EKS (الحوسبة)
├── S3/Cloud Storage (التخزين)
├── CloudFront/CDN (التوزيع)
├── Lambda/Cloud Functions (الحوسبة بدون خادم)
└── API Gateway (إدارة الـ APIs)
```

---

## بنية الذكاء الاصطناعي (AI Architecture)

### سلسلة النماذج الأساسية (Model Chaining)

#### الخطوة 1: استخلاص الميزات (Feature Extraction)
```python
# استخدام SAM/CLIP لعزل قطعة الملابس
from transformers import CLIPProcessor, CLIPModel
from segment_anything import SamPredictor

class GarmentExtractor:
    def __init__(self):
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        self.sam_predictor = SamPredictor.from_pretrained("sam-vit-huge")

    def extract_garment(self, image_path: str) -> dict:
        """
        استخراج ميزات الملابس من الصورة
        Returns: قاموس يحتوي على الميزات والقناع
        """
        # معالجة الصورة واستخراج الميزات
        pass
```

#### الخطوة 2: توليد الموديل (Model Generation)
```python
# استخدام Stable Diffusion XL لتوليد الموديل
from diffusers import StableDiffusionXLPipeline
import torch

class ModelGenerator:
    def __init__(self):
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        ).to("cuda")

    def generate_model(self, model_type: str, pose: str) -> Image:
        """
        توليد موديل بشري أو خفي
        Args:
            model_type: "human" أو "invisible"
            pose: وصف الوضعية المطلوبة
        """
        prompt = self._build_prompt(model_type, pose)
        return self.pipe(prompt).images[0]
```

#### الخطوة 3: التحكم بالهيكل (Pose Control)
```python
# استخدام ControlNet للتحكم بالوضعية
from controlnet_aux import OpenposeDetector
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline

class PoseController:
    def __init__(self):
        self.openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
        self.controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_openpose"
        )

    def extract_pose(self, model_image: Image) -> Image:
        """استخراج خريطة الوضعية من صورة الموديل"""
        return self.openpose(model_image)
```

#### الخطوة 4: دمج المنتج (Product Integration)
```python
# استخدام IP-Adapter و IGR لدمج الملابس
from ip_adapter import IPAdapter
from garment_restoration import IGRModel

class ProductIntegrator:
    def __init__(self):
        self.ip_adapter = IPAdapter.from_pretrained("h94/IP-Adapter")
        self.igr_model = IGRModel.from_pretrained("garment-restoration/igr")

    def integrate_product(self, garment_features: dict,
                         model_image: Image,
                         pose_map: Image) -> Image:
        """
        دمج قطعة الملابس مع الموديل مع الحفاظ على الدقة 100%
        """
        # تطبيق IP-Adapter للحفاظ على الميزات منخفضة المستوى
        adapted_model = self.ip_adapter.adapt(model_image, garment_features)

        # تطبيق IGR للحفاظ على الميزات عالية المستوى
        final_image = self.igr_model.restore(adapted_model, pose_map)

        return final_image
```

#### الخطوة 5: التحسين النهائي (Post-Processing)
```python
# تحسين الجودة النهائية
from realesrgan import RealESRGAN
from gfpgan import GFPGANer

class ImageEnhancer:
    def __init__(self):
        self.realesrgan = RealESRGAN.from_pretrained("realesrgan-x4plus")
        self.gfpgan = GFPGANer.from_pretrained("GFPGANv1.4")

    def enhance(self, image: Image) -> Image:
        """تحسين جودة الصورة النهائية"""
        # زيادة الدقة
        high_res = self.realesrgan.enhance(image)

        # تحسين الوجوه والتفاصيل
        enhanced = self.gfpgan.enhance(high_res)

        return enhanced
```

---

## هيكل قاعدة البيانات

### جداول PostgreSQL الأساسية

#### 1. جدول المستخدمين (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    user_type VARCHAR(50) DEFAULT 'individual', -- individual, business, enterprise
    credits_balance INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- فهرسة للأداء
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(user_type);
```

#### 2. جدول المهام (jobs)
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    celery_task_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending',
    model_type VARCHAR(50) DEFAULT 'invisible', -- invisible, human
    pose_id UUID REFERENCES poses(id),
    background_id UUID REFERENCES backgrounds(id),
    input_image_url TEXT,
    output_image_url TEXT,
    processing_time_seconds INTEGER,
    credits_used INTEGER DEFAULT 1,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    tenant_id UUID -- للمؤسسات (V1.1)
);

-- فهرسة للأداء
CREATE INDEX idx_jobs_user_status ON jobs(user_id, status);
CREATE INDEX idx_jobs_celery_id ON jobs(celery_task_id);
CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
```

#### 3. جدول المعاملات (transactions)
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50), -- credit_purchase, processing_fee, refund
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    credits_amount INTEGER,
    stripe_payment_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tenant_id UUID
);
```

---

## واجهات برمجة التطبيقات (APIs)

### نقاط النهاية الرئيسية

#### 1. رفع ومعالجة الصور
```python
# POST /api/v1/process
@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    model_type: str = Form("invisible"),
    pose_id: str = Form(None),
    background_id: str = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    رفع صورة وإنشاء مهمة معالجة
    """
    # حفظ الصورة في S3
    input_url = await upload_to_s3(file)

    # إنشاء مهمة Celery
    task = process_image_task.delay(
        user_id=str(current_user.id),
        input_url=input_url,
        model_type=model_type,
        pose_id=pose_id,
        background_id=background_id
    )

    # حفظ في قاعدة البيانات
    job = Job(
        user_id=current_user.id,
        celery_task_id=task.id,
        model_type=model_type,
        input_image_url=input_url
    )
    db.add(job)
    db.commit()

    return {"job_id": job.id, "task_id": task.id}
```

#### 2. التحقق من حالة المهمة
```python
# GET /api/v1/jobs/{job_id}
@app.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    الحصول على حالة مهمة المعالجة
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # التحقق من حالة Celery
    task_result = AsyncResult(job.celery_task_id)

    return {
        "job_id": job.id,
        "status": job.status,
        "progress": task_result.info.get('progress', 0) if task_result.info else 0,
        "output_url": job.output_image_url,
        "processing_time": job.processing_time_seconds
    }
```

#### 3. إدارة الاعتمادات (V1.0)
```python
# POST /api/v1/credits/purchase
@app.post("/credits/purchase")
async def purchase_credits(
    package_id: str,
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    شراء حزمة اعتمادات
    """
    package = get_credit_package(package_id)

    # إنشاء دفعة Stripe
    payment_intent = stripe.PaymentIntent.create(
        amount=package.price_cents,
        currency="eur",
        payment_method=payment_method_id,
        confirm=True
    )

    # تحديث رصيد المستخدم
    current_user.credits_balance += package.credits
    db.commit()

    # تسجيل المعاملة
    transaction = Transaction(
        user_id=current_user.id,
        transaction_type="credit_purchase",
        amount_cents=package.price_cents,
        credits_amount=package.credits,
        stripe_payment_id=payment_intent.id,
        status="completed"
    )
    db.add(transaction)
    db.commit()

    return {"success": True, "new_balance": current_user.credits_balance}
```

---

## إعدادات Celery للمعالجة غير المتزامنة

### ملف التكوين (celery_app.py)
```python
from celery import Celery
from kombu import Exchange, Queue

# إعداد Celery
app = Celery('modamoda_tasks')

# إعداد Redis كوسيط رسائل
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# إعداد قوائم الانتظار
app.conf.task_queues = (
    Queue('high_priority', Exchange('high_priority'), routing_key='high_priority'),
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('low_priority', Exchange('low_priority'), routing_key='low_priority'),
)

# إعداد المسلسل
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# إعدادات الأداء
app.conf.worker_prefetch_multiplier = 1  # مهمة واحدة لكل عامل
app.conf.task_acks_late = True
app.conf.worker_disable_rate_limits = False
```

### مهمة معالجة الصور (tasks.py)
```python
from celery_app import app
from ai_processor import AIProcessor
from database import get_db
import time

@app.task(bind=True)
def process_image_task(self, user_id: str, input_url: str,
                      model_type: str, pose_id: str = None,
                      background_id: str = None):
    """
    مهمة معالجة الصور بالذكاء الاصطناعي
    """
    start_time = time.time()

    try:
        # تحديث حالة المهمة
        self.update_state(state='PROGRESS', meta={'progress': 10})

        # تهيئة معالج AI
        processor = AIProcessor()

        # تحميل الصورة من S3
        input_image = download_from_s3(input_url)

        self.update_state(state='PROGRESS', meta={'progress': 30})

        # معالجة الصورة
        output_image = processor.process(
            input_image=input_image,
            model_type=model_type,
            pose_id=pose_id,
            background_id=background_id
        )

        self.update_state(state='PROGRESS', meta={'progress': 80})

        # رفع النتيجة إلى S3
        output_url = upload_to_s3(output_image, f"processed/{user_id}/")

        # تحديث قاعدة البيانات
        db = next(get_db())
        job = db.query(Job).filter(Job.celery_task_id == self.request.id).first()
        if job:
            job.status = 'completed'
            job.output_image_url = output_url
            job.processing_time_seconds = int(time.time() - start_time)
            job.completed_at = datetime.utcnow()
            db.commit()

        self.update_state(state='PROGRESS', meta={'progress': 100})

        return {
            'status': 'completed',
            'output_url': output_url,
            'processing_time': int(time.time() - start_time)
        }

    except Exception as e:
        # تحديث حالة الخطأ
        db = next(get_db())
        job = db.query(Job).filter(Job.celery_task_id == self.request.id).first()
        if job:
            job.status = 'failed'
            job.error_message = str(e)
            db.commit()

        raise self.retry(countdown=60, max_retries=3, exc=e)
```

---

## إعدادات الأمان والامتثال

### 1. تشفير البيانات
```python
# إعدادات تشفير البيانات الحساسة
from cryptography.fernet import Fernet
import os

# إنشاء مفتاح التشفير
def generate_key():
    return Fernet.generate_key()

# تشفير البيانات
def encrypt_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

# فك تشفير البيانات
def decrypt_data(encrypted_data: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

### 2. إدارة مفاتيح API (لـ BYOK)
```python
# نظام إدارة المفاتيح للمؤسسات
class APIKeyManager:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.kms_client = boto3.client('kms')

    def store_api_key(self, provider: str, api_key: str) -> str:
        """
        تخزين مفتاح API مشفر للعميل المؤسسي
        """
        # تشفير المفتاح
        encrypted_key = self.kms_client.encrypt(
            KeyId=self.get_tenant_key_id(),
            Plaintext=api_key
        )['CiphertextBlob']

        # حفظ في قاعدة البيانات
        api_key_record = APIKey(
            tenant_id=self.tenant_id,
            provider=provider,
            encrypted_key=encrypted_key.decode('utf-8'),
            created_at=datetime.utcnow()
        )
        db.add(api_key_record)
        db.commit()

        return api_key_record.id

    def get_api_key(self, provider: str) -> str:
        """
        استرجاع مفتاح API مفكوك للاستخدام
        """
        api_key_record = db.query(APIKey).filter(
            APIKey.tenant_id == self.tenant_id,
            APIKey.provider == provider
        ).first()

        if not api_key_record:
            raise ValueError(f"No API key found for provider: {provider}")

        # فك تشفير المفتاح
        decrypted_key = self.kms_client.decrypt(
            CiphertextBlob=api_key_record.encrypted_key.encode('utf-8')
        )['Plaintext']

        return decrypted_key.decode('utf-8')
```

---

## إعدادات الأداء والتوسع

### 1. إعدادات Docker
```dockerfile
# Dockerfile للخدمة الرئيسية
FROM python:3.11-slim

WORKDIR /app

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# تشغيل التطبيق
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. إعدادات Kubernetes للتوسع
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: modamoda-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: modamoda-backend
  template:
    metadata:
      labels:
        app: modamoda-backend
    spec:
      containers:
      - name: api
        image: modamoda/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 3. مراقبة الأداء
```python
# إعدادات Prometheus للمراقبة
from prometheus_client import Counter, Histogram, Gauge

# مقاييس الأداء
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')

# مقاييس الأعمال
IMAGES_PROCESSED = Counter('images_processed_total', 'Total images processed')
PROCESSING_TIME = Histogram('image_processing_duration_seconds', 'Image processing time')
CREDITS_USED = Counter('credits_used_total', 'Total credits consumed')
```

---

## خطة الاختبار والجودة

### 1. اختبارات الوحدة (Unit Tests)
```python
# اختبار معالج AI
def test_garment_extraction():
    extractor = GarmentExtractor()
    test_image = load_test_image("garment.jpg")

    result = extractor.extract_garment(test_image)

    assert "mask" in result
    assert "features" in result
    assert result["confidence"] > 0.8

# اختبار API
def test_image_processing_endpoint(client):
    # إنشاء مستخدم اختبار
    user = create_test_user()

    # رفع صورة اختبار
    with open("test_garment.jpg", "rb") as f:
        response = client.post(
            "/api/v1/process",
            files={"file": ("test.jpg", f, "image/jpeg")},
            headers={"Authorization": f"Bearer {user.token}"}
        )

    assert response.status_code == 200
    assert "job_id" in response.json()
```

### 2. اختبارات الأداء (Performance Tests)
```python
# اختبار الحمل
def test_high_load_processing():
    # محاكاة 100 مستخدم متزامن
    @pytest.mark.parametrize("num_users", [10, 50, 100])
    def test_concurrent_processing(num_users):
        # إنشاء مهام متعددة
        tasks = []
        for i in range(num_users):
            task = process_image_task.delay(
                user_id="test_user",
                input_url=f"test_image_{i}.jpg",
                model_type="invisible"
            )
            tasks.append(task)

        # انتظار اكتمال جميع المهام
        completed = 0
        for task in tasks:
            result = task.get(timeout=300)  # 5 دقائق timeout
            if result['status'] == 'completed':
                completed += 1

        # التأكد من نجاح 95% من المهام
        success_rate = completed / num_users
        assert success_rate >= 0.95
```

---

## خطة النشر والصيانة

### 1. بيئات النشر
```
Development → Staging → Production
    ↓           ↓          ↓
  Local      AWS/GCP    AWS/GCP
  Docker     Kubernetes  Kubernetes
  SQLite     PostgreSQL  PostgreSQL
```

### 2. CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        # أوامر النشر
        kubectl apply -f k8s/
        kubectl rollout restart deployment/modamoda-backend
```

### 3. مراقبة وصيانة
- **Sentry**: تتبع الأخطاء والاستثناءات
- **DataDog/New Relic**: مراقبة الأداء والصحة
- **ELK Stack**: تحليل السجلات والبحث
- **Automated Backups**: نسخ احتياطي يومي لقاعدة البيانات

---

*هذه المواصفات التقنية الشاملة توفر الأساس المتين لبناء وتشغيل منصة Modamoda Invisible Mannequin بكفاءة واحترافية.*
