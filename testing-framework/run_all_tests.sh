#!/bin/bash
#
# Run all AI conversation tests sequentially
#

set -e

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test scenarios in order
scenarios=(
    "02_regular_customer.yaml"
    "04_vip_demanding_customer.yaml"
    "05_order_tracking.yaml"
    "07_modify_order.yaml"
    "08_order_cancellation.yaml"
    "09_check_working_hours.yaml"
    "10_existing_customer_reorder.yaml"
    "11_track_with_tracking_id.yaml"
    "12_multiple_orders_history.yaml"
)

# Track results
total=0
passed=0
failed=0

echo "======================================"
echo "🧪 RUNNING ALL AI CONVERSATION TESTS"
echo "======================================"
echo ""

for scenario in "${scenarios[@]}"; do
    total=$((total + 1))
    echo -e "${BLUE}▶ Running test $total/${#scenarios[@]}: $scenario${NC}"

    if python3 test_orchestrator.py "$scenario"; then
        passed=$((passed + 1))
        echo -e "${GREEN}✅ PASSED: $scenario${NC}"
    else
        failed=$((failed + 1))
        echo -e "${RED}❌ FAILED: $scenario${NC}"
    fi

    echo ""
    echo "Waiting 5 seconds before next test (API rate limiting)..."
    sleep 5
done

# Summary
echo "======================================"
echo "📊 TEST SUITE SUMMARY"
echo "======================================"
echo -e "Total tests:  ${total}"
echo -e "${GREEN}Passed:       ${passed}${NC}"
echo -e "${RED}Failed:       ${failed}${NC}"
echo -e "Success rate: $((passed * 100 / total))%"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
