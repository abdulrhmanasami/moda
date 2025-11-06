# @Study:ST-004 @Study:ST-008
#!/usr/bin/env bash

set -euo pipefail

THRESHOLD="${COVERAGE_THRESHOLD:-0.80}"

ACTUAL=$(jq -r '.total | tonumber' governance/out/coverage.json 2>/dev/null || echo 0)

# Calculate percentages
ACTUAL_PERCENT=$(awk "BEGIN{printf \"%.1f\", $ACTUAL * 100}")
THRESHOLD_PERCENT=$(awk "BEGIN{printf \"%.1f\", $THRESHOLD * 100}")

# Generate detailed report
cat > coverage_report.txt << EOF
📊 **Coverage Report**
- **Current Coverage:** $ACTUAL_PERCENT%
- **Required Threshold:** $THRESHOLD_PERCENT%
- **Status:** $(echo "$ACTUAL >= $THRESHOLD" | bc -l >/dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED")

EOF

# Check threshold
if ! echo "$ACTUAL >= $THRESHOLD" | bc -l >/dev/null 2>&1; then
  echo "❌ Coverage $ACTUAL_PERCENT% < $THRESHOLD_PERCENT%" >&2;
  exit 1;
fi

echo "✅ Coverage $ACTUAL_PERCENT% ≥ $THRESHOLD_PERCENT%"
