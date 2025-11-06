#!/usr/bin/env bash

set -euo pipefail

CHART_DIR="infrastructure/helm/modamoda"
VALUES="${CHART_DIR}/values-secure.yaml"
TMP_DIR="$(mktemp -d)"
RENDERED="${TMP_DIR}/rendered.yaml"
RULES_OUT="${TMP_DIR}/rules.generated.yaml"

# Render all helm manifests
helm template modamoda "${CHART_DIR}" -f "${VALUES}" > "${RENDERED}"

# Extract PrometheusRule->spec.groups into a plain Prometheus rules file
# Requires yq v4+
yq -o=yaml '
  ( .kind == "List" ) as $isList
  | ( $isList
      ? .items[] 
      : . ) 
  | select(.kind == "PrometheusRule")
  | .spec
  | { groups: .groups }
' "${RENDERED}" > "${RULES_OUT}"

echo "${RULES_OUT}"
