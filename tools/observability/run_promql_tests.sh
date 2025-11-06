#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="${SCRIPT_DIR}/tests"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Running PromQL SLO Tests..."
echo "================================="

# Check if promtool is available
if ! command -v promtool &> /dev/null; then
    echo -e "${RED}❌ promtool not found. Please install Prometheus first.${NC}"
    echo "   Download from: https://prometheus.io/download/"
    exit 1
fi

PASSED=0
FAILED=0
TOTAL=0

# Function to run a test
run_test() {
    local test_file="$1"
    local test_name=$(basename "$test_file" .yml)

    echo -e "\n${YELLOW}🧪 Running test: ${test_name}${NC}"

    if promtool test rules "$test_file"; then
        echo -e "${GREEN}✅ PASSED: ${test_name}${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED: ${test_name}${NC}"
        ((FAILED++))
    fi
    ((TOTAL++))
}

# Run all tests
for test_file in "${TEST_DIR}"/test_*.yml; do
    if [[ -f "$test_file" ]]; then
        run_test "$test_file"
    fi
done

# Summary
echo ""
echo "================================="
echo -e "${YELLOW}📊 Test Results Summary:${NC}"
echo "Total tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    echo -e "${RED}❌ Some tests failed. Please review the PromQL rules and test data.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All tests passed! SLO rules are working correctly.${NC}"
    echo ""
    echo -e "${GREEN}🎉 ORI (Operational Readiness Index) = 100%${NC}"
fi
