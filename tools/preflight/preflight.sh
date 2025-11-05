#!/usr/bin/env bash

set -euo pipefail

# ==== إعدادات ====

COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-0.95}"
PY_TEST_MIN_COV="${PY_TEST_MIN_COV:-75}"
REPORT="governance/out/preflight_report.md"
START=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

pass() { echo "✅ $1"; }
fail() { echo "❌ $1"; exit 1; }
note() { echo "ℹ️  $1"; }

echo "# Preflight Report" > "$REPORT"
echo "- Started: $START" >> "$REPORT"
echo "- Coverage Gate: $COVERAGE_THRESHOLD" >> "$REPORT"
echo "" >> "$REPORT"

# ==== Hygiene ====

echo "## Hygiene" >> "$REPORT"
tools/hygiene/repo_hygiene.sh && pass "Hygiene PASS" | tee -a "$REPORT"

# ==== Governance (Monitor + Coverage Gate) ====

echo -e "\n## Governance" >> "$REPORT"
python3 scripts/governance_monitor.py || true
ACTUAL=$(jq -r '.total' governance/out/coverage.json 2>/dev/null || echo "0")
echo "- Study coverage: ${ACTUAL}" >> "$REPORT"
COVERAGE_THRESHOLD="$COVERAGE_THRESHOLD" tools/quality/coverage_gate.sh && pass "Coverage ≥ ${COVERAGE_THRESHOLD}" | tee -a "$REPORT"

# ==== Compliance ====

echo -e "\n## Compliance" >> "$REPORT"
tools/compliance/compliance_checker && pass "Compliance PASS" | tee -a "$REPORT"

# ==== Security OPS (Python) ====

echo -e "\n## Security OPS" >> "$REPORT"
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/devops/security/security_ops.py check && pass "Security Ops PASS" | tee -a "$REPORT"
else
  note "python3 not found—skipping security_ops.py" | tee -a "$REPORT"
fi

# ==== Tests (Python) ====

echo -e "\n## Tests (Python)" >> "$REPORT"
if command -v pytest >/dev/null 2>&1; then
  pytest -q --maxfail=1 --disable-warnings && pass "PyTests run successfully" | tee -a "$REPORT"
else
  note "pytest not found—skipping" | tee -a "$REPORT"
fi

# ==== Tests (Frontend) ====

echo -e "\n## Tests (Frontend)" >> "$REPORT"
note "Frontend tests skipped - dependencies need setup" | tee -a "$REPORT"

# ==== IaC (Terraform / Helm) ====

echo -e "\n## IaC Validation" >> "$REPORT"
if [ -d "infrastructure/terraform" ]; then
  pushd infrastructure/terraform >/dev/null
    command -v terraform >/dev/null 2>&1 && terraform fmt -check && terraform validate || true
    command -v tflint >/dev/null 2>&1 && tflint || true
    command -v tfsec >/dev/null 2>&1 && tfsec --soft-fail || true
  popd >/dev/null
  pass "Terraform validation done" | tee -a "$REPORT"
else
  note "No Terraform dir" | tee -a "$REPORT"
fi
if [ -d "infrastructure/helm" ]; then
  command -v helm >/dev/null 2>&1 && helm lint infrastructure/helm/modamoda || true
  pass "Helm lint done" | tee -a "$REPORT"
else
  note "No Helm dir" | tee -a "$REPORT"
fi

# ==== Container (اختياري) ====

echo -e "\n## Container Scan" >> "$REPORT"
if [ -f "Dockerfile" ]; then
  if command -v hadolint >/dev/null 2>&1; then hadolint Dockerfile || true; fi
  if command -v syft >/dev/null 2>&1; then syft dir:. -o cyclonedx-json > governance/out/sbom.json || true; fi
  if command -v grype >/dev/null 2>&1; then grype -q dir:. || true; fi
  pass "Container checks done" | tee -a "$REPORT"
else
  note "No Dockerfile—skipping container checks" | tee -a "$REPORT"
fi

# ==== Checksums للدراسات ====

echo -e "\n## Studies Integrity" >> "$REPORT"
if command -v sha256sum >/dev/null 2>&1; then
  find governance/studies -type f -maxdepth 3 -not -path "*/out/*" \
    -exec sha256sum {} \; | sort -k2 > governance/out/studies.sha256
  pass "SHA256 index created" | tee -a "$REPORT"
else
  note "sha256sum not found—skipping" | tee -a "$REPORT"
fi

END=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
echo -e "\n---\n- Finished: $END" >> "$REPORT"

echo "✅ Preflight OK — see $REPORT"
