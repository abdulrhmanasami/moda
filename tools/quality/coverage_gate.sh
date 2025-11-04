# @Study:ST-004 @Study:ST-008
#!/usr/bin/env bash

set -euo pipefail

THRESHOLD="${COVERAGE_THRESHOLD:-0.80}"

ACTUAL=$(jq -r '.total | tonumber' governance/out/coverage.json 2>/dev/null || echo 0)

awk "BEGIN{exit !( $ACTUAL >= $THRESHOLD )}" || { echo "❌ Coverage $ACTUAL < $THRESHOLD"; exit 1; }

echo "✅ Coverage $ACTUAL ≥ $THRESHOLD"
