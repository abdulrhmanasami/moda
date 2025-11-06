#!/usr/bin/env bash
# @Study:ST-012 @Study:ST-019
set -euo pipefail

# Infrastructure Deployment Script
# Deploys Modamoda infrastructure using Terraform and Helm

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infrastructure"
TERRAFORM_DIR="$INFRA_DIR/terraform"
HELM_DIR="$INFRA_DIR/helm"

ENVIRONMENT="${ENVIRONMENT:-development}"
REGION="${AWS_REGION:-us-east-1}"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

error() {
    log "❌ ERROR: $*" >&2
    exit 1
}

success() {
    log "✅ SUCCESS: $*" >&2
}

check_dependencies() {
    log "🔍 Checking dependencies..."

    command -v terraform >/dev/null 2>&1 || error "Terraform is not installed"
    command -v helm >/dev/null 2>&1 || error "Helm is not installed"
    command -v kubectl >/dev/null 2>&1 || error "kubectl is not installed"
    command -v aws >/dev/null 2>&1 || error "AWS CLI is not installed"

    # Check AWS credentials
    aws sts get-caller-identity >/dev/null 2>&1 || error "AWS credentials not configured"

    success "All dependencies are available"
}

terraform_plan() {
    log "🏗️ Planning Terraform infrastructure..."

    cd "$TERRAFORM_DIR"

    # Initialize Terraform
    terraform init

    # Create terraform.tfvars
    cat > terraform.tfvars << EOF
aws_region = "$REGION"
environment = "$ENVIRONMENT"
vpc_cidr = "10.0.0.0/16"
db_name = "modamoda"
db_username = "$(openssl rand -hex 8)"
db_password = "$(openssl rand -hex 16)"
db_instance_class = "db.t3.micro"
redis_node_type = "cache.t3.micro"
redis_num_cache_nodes = 1
s3_bucket_name = "modamoda-storage-${ENVIRONMENT}-$(openssl rand -hex 4)"
app_image = "modamoda/backend:latest"
app_count = 2
app_port = 8000
fargate_cpu = 256
fargate_memory = 512
EOF

    # Plan infrastructure
    terraform plan -out=tfplan

    success "Terraform plan created successfully"
}

terraform_apply() {
    log "🚀 Applying Terraform infrastructure..."

    cd "$TERRAFORM_DIR"

    terraform apply tfplan

    success "Infrastructure deployed successfully"
}

helm_deploy() {
    log "⚓ Deploying Helm charts..."

    # Get infrastructure outputs
    cd "$TERRAFORM_DIR"
    DATABASE_URL=$(terraform output -raw rds_endpoint)
    REDIS_URL=$(terraform output -raw redis_endpoint)

    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}"

    cd "$HELM_DIR"

    # Create secrets file
    cat > modamoda/secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: modamoda-secrets
type: Opaque
data:
  database-url: $(echo -n "postgresql://modamoda_user:$DATABASE_PASSWORD@$DATABASE_URL/modamoda" | base64 -w 0)
  redis-url: $(echo -n "$REDIS_URL" | base64 -w 0)
  secret-key: $(echo -n "$SECRET_KEY" | base64 -w 0)
  jwt-secret-key: $(echo -n "$JWT_SECRET_KEY" | base64 -w 0)
  openai-api-key: $(echo -n "$OPENAI_API_KEY" | base64 -w 0)
EOF

    # Deploy Helm chart
    helm upgrade --install modamoda ./modamoda \
        --namespace modamoda \
        --create-namespace \
        --set global.environment="$ENVIRONMENT" \
        --set global.domain="modamoda-${ENVIRONMENT}.local" \
        --wait

    success "Helm charts deployed successfully"
}

verify_deployment() {
    log "🔍 Verifying deployment..."

    # Wait for pods to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/modamoda-backend -n modamoda
    kubectl wait --for=condition=available --timeout=300s deployment/modamoda-frontend -n modamoda

    # Check pod status
    kubectl get pods -n modamoda

    # Test application health
    BACKEND_POD=$(kubectl get pods -n modamoda -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
    kubectl exec -n modamoda "$BACKEND_POD" -- curl -f http://localhost:8000/health

    success "Deployment verification completed"
}

cleanup() {
    log "🧹 Cleaning up temporary files..."

    # Remove terraform.tfvars (contains sensitive data)
    [[ -f "$TERRAFORM_DIR/terraform.tfvars" ]] && rm "$TERRAFORM_DIR/terraform.tfvars"

    # Remove secrets file
    [[ -f "$HELM_DIR/modamoda/secrets.yaml" ]] && rm "$HELM_DIR/modamoda/secrets.yaml"

    success "Cleanup completed"
}

case "${1:-deploy}" in
    "check")
        check_dependencies
        ;;
    "plan")
        check_dependencies
        terraform_plan
        ;;
    "apply")
        check_dependencies
        terraform_apply
        ;;
    "helm")
        check_dependencies
        helm_deploy
        ;;
    "verify")
        verify_deployment
        ;;
    "cleanup")
        cleanup
        ;;
    "deploy")
        log "🚀 Starting full deployment process..."
        check_dependencies
        terraform_plan
        read -p "Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            terraform_apply
            helm_deploy
            verify_deployment
            cleanup
            success "Full deployment completed successfully! 🎉"
        else
            log "Deployment cancelled by user"
        fi
        ;;
    "destroy")
        log "⚠️  WARNING: This will destroy all infrastructure!"
        read -p "Are you sure? Type 'yes' to continue: " -r
        if [[ $REPLY == "yes" ]]; then
            cd "$TERRAFORM_DIR"
            terraform destroy
            success "Infrastructure destroyed"
        fi
        ;;
    *)
        echo "Usage: $0 {check|plan|apply|helm|verify|cleanup|deploy|destroy}"
        echo ""
        echo "Commands:"
        echo "  check   - Check dependencies and AWS access"
        echo "  plan    - Plan infrastructure changes"
        echo "  apply   - Apply infrastructure changes"
        echo "  helm    - Deploy Helm charts"
        echo "  verify  - Verify deployment health"
        echo "  cleanup - Clean up temporary files"
        echo "  deploy  - Full deployment (plan + apply + helm + verify)"
        echo "  destroy - Destroy all infrastructure"
        ;;
esac
