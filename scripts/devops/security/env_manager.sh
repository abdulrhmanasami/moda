#!/usr/bin/env bash
# @Study:ST-013 @Study:ST-019
set -euo pipefail

# نظام إدارة البيئة الآمن - Secure Environment Manager
# يوفر إعداد آمن لمتغيرات البيئة

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
BACKUP_DIR="$PROJECT_ROOT/scripts/devops/security/backups"
KEY_MANAGER="$PROJECT_ROOT/scripts/devops/keys/key_manager.py"

mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

backup_env() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/env_backup_$timestamp"

    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "$backup_file"
        log "✅ Environment backed up to: $backup_file"
    fi
}

generate_secure_value() {
    local length=${1:-32}
    python3 -c "import secrets; print(secrets.token_hex($length))"
}

setup_secure_env() {
    log "🔐 Setting up secure environment..."

    backup_env

    # إنشاء أو تحديث ملف البيئة الآمن
    cat > "$ENV_FILE" << EOF
# @Study:ST-013 @Study:ST-019
# ملف البيئة الآمن - تم إنشاؤه بواسطة Security OPS
# $(date)

# قاعدة البيانات
DATABASE_URL=postgresql://modamoda_user:$(generate_secure_value 16)@postgres/modamoda_prod

# Redis للذاكرة المؤقتة والمهام
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# الأمان والمصادقة
SECRET_KEY=$(generate_secure_value 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# JWT
JWT_SECRET_KEY=$(generate_secure_value 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=10080

# الذكاء الاصطناعي (يجب تعيينها يدوياً)
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
REPLICATE_API_TOKEN=your-replicate-api-token-here

# تخزين السحابة (يجب تعيينها يدوياً)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=modamoda-secure-storage

# التطبيق
ENVIRONMENT=production
DEBUG=false
API_V1_STR=/api/v1
PROJECT_NAME=Modamoda Invisible Mannequin
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# الأداء
MAX_WORKERS=4
REQUEST_TIMEOUT=300
WORKER_TIMEOUT=600

# الحوكمة والمراقبة
GOVERNANCE_ALERT_EMAIL=security@modamoda.com
COMPLIANCE_THRESHOLD=95
GOVERNANCE_LOG_LEVEL=INFO

# المراقبة والسجلات
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO
JSON_LOGS=true

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://modamoda.com"]

EOF

    chmod 600 "$ENV_FILE"
    log "✅ Secure environment file created: $ENV_FILE"
    log "⚠️  IMPORTANT: Update AI and Cloud keys manually"
}

validate_env() {
    log "🔍 Validating environment configuration..."

    if [[ ! -f "$ENV_FILE" ]]; then
        log "❌ Environment file not found: $ENV_FILE"
        return 1
    fi

    local issues=0

    # التحقق من القيم الافتراضية الخطرة
    while IFS='=' read -r key value; do
        [[ $key =~ ^[[:space:]]*# ]] && continue  # تخطي التعليقات
        [[ -z "$key" ]] && continue  # تخطي الأسطر الفارغة

        # فحص القيم الافتراضية
        if [[ "$value" =~ your-.*-key ]] || [[ "$value" =~ your-.*-token ]] || [[ "$value" =~ your-.*-dsn ]]; then
            log "⚠️  WARNING: Default value detected for $key"
            ((issues++))
        fi
    done < "$ENV_FILE"

    # التحقق من المفاتيح المطلوبة
    local required_keys=(
        "SECRET_KEY"
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET_KEY"
    )

    for key in "${required_keys[@]}"; do
        if ! grep -q "^$key=" "$ENV_FILE"; then
            log "❌ MISSING: Required key $key not found"
            ((issues++))
        fi
    done

    if [[ $issues -eq 0 ]]; then
        log "✅ Environment validation passed"
        return 0
    else
        log "❌ Environment validation failed: $issues issues found"
        return 1
    fi
}

rotate_secrets() {
    log "🔄 Rotating environment secrets..."

    backup_env

    # حفظ القيم التي لا يجب تغييرها
    local preserve_keys=("OPENAI_API_KEY" "HUGGINGFACE_API_KEY" "REPLICATE_API_TOKEN" "AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "SENTRY_DSN")

    declare -A preserved_values

    for key in "${preserve_keys[@]}"; do
        if grep -q "^$key=" "$ENV_FILE" 2>/dev/null; then
            preserved_values[$key]=$(grep "^$key=" "$ENV_FILE" | cut -d'=' -f2-)
        fi
    done

    # إعادة إنشاء الملف مع قيم جديدة
    setup_secure_env

    # إعادة القيم المحفوظة
    for key in "${!preserved_values[@]}"; do
        sed -i.bak "s|^$key=.*|$key=${preserved_values[$key]}|" "$ENV_FILE"
        rm "${ENV_FILE}.bak"
    done

    log "✅ Secrets rotated successfully"
}

show_status() {
    log "📊 Environment Security Status:"

    if [[ -f "$ENV_FILE" ]]; then
        local file_perms=$(stat -c %a "$ENV_FILE" 2>/dev/null || stat -f %A "$ENV_FILE")
        echo "  Environment File: ✅ Exists (permissions: $file_perms)"

        local backup_count=$(find "$BACKUP_DIR" -name "env_backup_*" 2>/dev/null | wc -l)
        echo "  Backups Available: $backup_count"

        if validate_env >/dev/null 2>&1; then
            echo "  Validation: ✅ Passed"
        else
            echo "  Validation: ❌ Failed"
        fi
    else
        echo "  Environment File: ❌ Not found"
    fi

    if [[ -f "$KEY_MANAGER" ]]; then
        echo "  Key Manager: ✅ Available"
    else
        echo "  Key Manager: ❌ Not found"
    fi
}

case "${1:-help}" in
    "setup")
        setup_secure_env
        ;;
    "validate")
        validate_env
        ;;
    "rotate")
        rotate_secrets
        ;;
    "backup")
        backup_env
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        echo "Usage: $0 {setup|validate|rotate|backup|status|help}"
        echo ""
        echo "Commands:"
        echo "  setup    - Create secure environment file"
        echo "  validate - Validate environment configuration"
        echo "  rotate   - Rotate secrets while preserving API keys"
        echo "  backup   - Create backup of current environment"
        echo "  status   - Show environment security status"
        echo "  help     - Show this help"
        ;;
esac
