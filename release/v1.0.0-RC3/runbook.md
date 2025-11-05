# 🚀 Modamoda v1.0.0-RC1 Deployment Runbook

## Prerequisites

- Docker & Docker Compose
- Terraform v1.5+
- Helm v3.12+
- kubectl configured for target cluster
- AWS CLI configured (if deploying to AWS)

## Quick Deploy (5 minutes)

```bash
# 1. Extract package
unzip modamoda-v1.0.0-RC1.zip -d modamoda/
cd modamoda

# 2. Configure environment
cp env.example .env
# Edit .env with production values

# 3. Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# 4. Deploy application
cd ../helm
helm install modamoda ./modamoda -f values-prod.yaml

# 5. Verify deployment
kubectl get pods -n modamoda
kubectl get services -n modamoda
```

## Detailed Steps

### 1. Infrastructure Setup

```bash
# VPC, RDS, Redis, EKS setup
cd infrastructure/terraform
terraform workspace select prod  # or create new
terraform apply -var-file=prod.tfvars
```

### 2. Application Deployment

```bash
# Deploy via Helm
helm upgrade --install modamoda ./infrastructure/helm/modamoda \
  --namespace modamoda \
  --create-namespace \
  --values infrastructure/helm/modamoda/values-prod.yaml
```

### 3. Database Migration

```bash
# Run database migrations
kubectl exec -n modamoda deployment/modamoda-backend -- python scripts/migrate.py
```

### 4. Health Checks

```bash
# API health check
curl https://api.modamoda.com/health

# Frontend check
curl https://app.modamoda.com

# Monitoring
kubectl logs -n modamoda deployment/modamoda-backend -f
```

## Monitoring & Alerts

- Prometheus/Grafana dashboards auto-deployed
- AlertManager configured for critical alerts
- Log aggregation via Loki

## Rollback Ready

If issues detected, see `rollback_plan.md`

---

**Estimated Deploy Time**: 15-30 minutes
**Zero-downtime**: Yes (blue-green deployment)
