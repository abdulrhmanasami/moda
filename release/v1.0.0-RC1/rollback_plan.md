# 🔄 Modamoda Emergency Rollback Plan

## 🚨 When to Rollback

- Application errors >5% of requests
- Database connection failures
- Critical security vulnerability
- Performance degradation (>2s response time)
- Infrastructure issues (high CPU/memory)

## ⚡ Quick Rollback (2 minutes)

```bash
# Option 1: Helm rollback (recommended)
helm rollback modamoda 1 -n modamoda

# Option 2: Blue-green switch
kubectl patch service modamoda-service -n modamoda -p '{"spec":{"selector":{"version":"v0.9.0"}}}'

# Option 3: Scale down new deployment
kubectl scale deployment modamoda-backend-v1 -n modamoda --replicas=0
kubectl scale deployment modamoda-backend-v0-9 -n modamoda --replicas=3
```

## 📋 Detailed Rollback Procedure

### Step 1: Assess Situation

```bash
# Check current status
kubectl get pods -n modamoda
kubectl get deployments -n modamoda

# Check logs
kubectl logs -n modamoda deployment/modamoda-backend --tail=100

# Check metrics
kubectl exec -n monitoring prometheus-pod -- promtool query 'up'
```

### Step 2: Execute Rollback

```bash
# Method 1: Helm rollback (safest)
helm history modamoda -n modamoda
helm rollback modamoda <previous_revision> -n modamoda

# Method 2: Manual deployment rollback
kubectl set image deployment/modamoda-backend app=modamoda:v0.9.0 -n modamoda
kubectl rollout status deployment/modamoda-backend -n modamoda
```

### Step 3: Database Rollback (if needed)

```bash
# Only if schema changes caused issues
kubectl exec -n modamoda deployment/modamoda-backend -- python scripts/rollback_migration.py
```

### Step 4: Verify Rollback Success

```bash
# Health checks
curl https://api.modamoda.com/health

# Traffic verification
kubectl get hpa -n modamoda

# Alert verification
# Check that critical alerts are resolved
```

## 🛡️ Safety Measures

- **Zero-downtime**: All rollbacks maintain service availability
- **Database safety**: Schema rollbacks only when necessary
- **Monitoring preserved**: Metrics and logs remain active during rollback
- **Gradual rollout**: Can rollback percentage of traffic if needed

## 📞 Emergency Contacts

- **DevOps Lead**: +1-XXX-XXX-XXXX
- **Database Admin**: +1-XXX-XXX-XXXX
- **Security Team**: +1-XXX-XXX-XXXX

## ⏱️ Timeline

- **Detection**: < 1 minute (monitoring alerts)
- **Decision**: < 5 minutes (incident response team)
- **Execution**: < 2 minutes (automated rollback)
- **Verification**: < 5 minutes (health checks)

---

**Tested**: This rollback plan has been validated in staging environment.
**Last Updated**: 2025-11-05
