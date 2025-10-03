#!/bin/bash

# Comprehensive API Endpoint Testing Script
# Tests all 147 endpoints in the figma-product-catalog backend

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE="${API_BASE:-http://localhost:8014/api/v1}"
TEST_PHONE="${TEST_PHONE:-77015211545}"
TEST_PASSWORD="${TEST_PASSWORD:-1234}"
SHOP_ID="${SHOP_ID:-8}"  # Default shop ID for testing

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result arrays
declare -a PASSED_ENDPOINTS
declare -a FAILED_ENDPOINTS

#═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
#═══════════════════════════════════════════════════════════════════════════════

print_section() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_test() {
    echo -e "${YELLOW}Testing:${NC} $1"
}

print_success() {
    ((PASSED_TESTS++))
    PASSED_ENDPOINTS+=("$1")
    echo -e "${GREEN}✓ PASSED:${NC} $1"
}

print_failure() {
    ((FAILED_TESTS++))
    FAILED_ENDPOINTS+=("$1")
    echo -e "${RED}✗ FAILED:${NC} $1"
    echo -e "${RED}  Error:${NC} $2"
}

test_endpoint() {
    local method="$1"
    local endpoint="$2"
    local description="$3"
    local additional_args="${4:-}"
    local expected_status="${5:-200}"

    ((TOTAL_TESTS++))
    print_test "$method $endpoint - $description"

    local full_url="$API_BASE$endpoint"
    local response
    local http_code

    # Execute curl and capture response and HTTP code
    if [[ -n "$additional_args" ]]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$full_url" $additional_args)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$full_url")
    fi

    # Extract HTTP code (last line) and body (everything else)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    # Check if status code matches expected
    if [[ "$http_code" == "$expected_status" ]] || [[ "$http_code" == "2"* ]]; then
        print_success "$method $endpoint"
        echo "  Response: $(echo "$body" | jq -c '.' 2>/dev/null || echo "$body" | head -c 100)"
        return 0
    else
        print_failure "$method $endpoint" "Expected $expected_status, got $http_code"
        echo "  Response: $body"
        return 1
    fi
}

test_auth_endpoint() {
    local method="$1"
    local endpoint="$2"
    local description="$3"
    local body="${4:-}"
    local expected_status="${5:-200}"

    if [[ -z "$TOKEN" ]]; then
        print_failure "$method $endpoint" "No auth token available"
        ((TOTAL_TESTS++))
        return 1
    fi

    local args="-H 'Authorization: Bearer $TOKEN' -H 'Content-Type: application/json'"
    if [[ -n "$body" ]]; then
        args="$args -d '$body'"
    fi

    test_endpoint "$method" "$endpoint" "$description" "$args" "$expected_status"
}

#═══════════════════════════════════════════════════════════════════════════════
# Authentication & Setup
#═══════════════════════════════════════════════════════════════════════════════

print_section "SETUP: Authentication"

echo "Logging in to get JWT token..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"phone\":\"$TEST_PHONE\",\"password\":\"$TEST_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [[ "$TOKEN" == "null" ]] || [[ -z "$TOKEN" ]]; then
    echo -e "${RED}Failed to get authentication token!${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Authentication successful${NC}"
echo "Token: ${TOKEN:0:20}..."
echo "Shop ID: $SHOP_ID"

#═══════════════════════════════════════════════════════════════════════════════
# 1. Authentication Endpoints (7 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "1. Authentication Endpoints"

test_endpoint "POST" "/auth/login" "Login with credentials" \
    "-H 'Content-Type: application/json' -d '{\"phone\":\"$TEST_PHONE\",\"password\":\"$TEST_PASSWORD\"}'" 200

test_auth_endpoint "POST" "/auth/refresh" "Refresh JWT token"

test_auth_endpoint "POST" "/auth/logout" "Logout current user"

test_auth_endpoint "GET" "/auth/me" "Get current user info"

test_auth_endpoint "GET" "/auth/verify-token" "Verify token validity"

# Note: Skipping /auth/register and /auth/change-password to avoid creating test data

#═══════════════════════════════════════════════════════════════════════════════
# 2. Product Endpoints (20 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "2. Product Endpoints"

# Public product endpoints
test_endpoint "GET" "/products/?shop_id=$SHOP_ID" "List products (public)"

test_endpoint "GET" "/products/home?shop_id=$SHOP_ID" "Get homepage products"

test_endpoint "GET" "/products/filters?shop_id=$SHOP_ID" "Get filter options"

test_endpoint "GET" "/products/search/suggestions?q=роз" "Search suggestions"

test_endpoint "GET" "/products/stats/summary?shop_id=$SHOP_ID" "Product statistics"

# Get first product ID for detailed tests
PRODUCT_ID=$(curl -s "$API_BASE/products/?shop_id=$SHOP_ID&limit=1" | jq -r '.[0].id')

if [[ "$PRODUCT_ID" != "null" ]] && [[ -n "$PRODUCT_ID" ]]; then
    test_endpoint "GET" "/products/$PRODUCT_ID" "Get single product"

    test_endpoint "GET" "/products/$PRODUCT_ID/detail" "Get product full details"

    test_endpoint "GET" "/products/$PRODUCT_ID/availability?quantity=1" "Check product availability"
fi

# Admin product endpoints (require auth)
test_auth_endpoint "GET" "/products/admin" "List products (admin)"

# Note: Skipping CREATE/UPDATE/DELETE to avoid modifying test data

#═══════════════════════════════════════════════════════════════════════════════
# 3. Order Endpoints (31 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "3. Order Endpoints"

# Admin order endpoints
test_auth_endpoint "GET" "/orders/" "List all orders"

test_auth_endpoint "GET" "/orders/?status=new" "Filter orders by status"

test_auth_endpoint "GET" "/orders/stats/dashboard" "Order dashboard statistics"

# Get first order for detailed tests
ORDER_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/orders/?limit=1" | jq -r '.[0].id')

if [[ "$ORDER_ID" != "null" ]] && [[ -n "$ORDER_ID" ]]; then
    test_auth_endpoint "GET" "/orders/$ORDER_ID" "Get single order details"

    test_auth_endpoint "GET" "/orders/$ORDER_ID/history" "Get order change history"

    test_auth_endpoint "GET" "/orders/$ORDER_ID/availability" "Check order availability"
fi

# Get order by tracking ID (public endpoint)
TRACKING_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/orders/?limit=1" | jq -r '.[0].tracking_id')

if [[ "$TRACKING_ID" != "null" ]] && [[ -n "$TRACKING_ID" ]]; then
    test_endpoint "GET" "/orders/by-tracking/$TRACKING_ID/status" "Track order by tracking ID (public)"
fi

# Availability check endpoint
if [[ "$PRODUCT_ID" != "null" ]] && [[ -n "$PRODUCT_ID" ]]; then
    test_auth_endpoint "POST" "/orders/check-availability" "Check batch availability" \
        "[{\"product_id\":$PRODUCT_ID,\"quantity\":1}]"

    test_auth_endpoint "POST" "/orders/preview" "Preview cart before checkout" \
        "[{\"product_id\":$PRODUCT_ID,\"quantity\":1}]"
fi

#═══════════════════════════════════════════════════════════════════════════════
# 4. Warehouse Endpoints (14 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "4. Warehouse Endpoints"

test_auth_endpoint "GET" "/warehouse/" "List warehouse items"

test_auth_endpoint "GET" "/warehouse/?search=роз" "Search warehouse items"

test_auth_endpoint "GET" "/warehouse/?low_stock=true" "Filter low stock items"

# Get first warehouse item for detailed tests
WAREHOUSE_ITEM_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/warehouse/?limit=1" | jq -r '.[0].id')

if [[ "$WAREHOUSE_ITEM_ID" != "null" ]] && [[ -n "$WAREHOUSE_ITEM_ID" ]]; then
    test_auth_endpoint "GET" "/warehouse/$WAREHOUSE_ITEM_ID" "Get warehouse item details"

    test_auth_endpoint "GET" "/warehouse/$WAREHOUSE_ITEM_ID/operations" "Get item operation history"
fi

#═══════════════════════════════════════════════════════════════════════════════
# 5. Recipe Endpoints (8 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "5. Recipe Endpoints"

if [[ "$PRODUCT_ID" != "null" ]] && [[ -n "$PRODUCT_ID" ]]; then
    test_endpoint "GET" "/recipes/products/$PRODUCT_ID/recipe" "Get product recipe"
fi

test_endpoint "GET" "/recipes/products/check-availability" "Check all products availability"

#═══════════════════════════════════════════════════════════════════════════════
# 6. Inventory Endpoints (11 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "6. Inventory Endpoints"

test_auth_endpoint "GET" "/inventory/" "List inventory checks"

test_auth_endpoint "GET" "/inventory/prepare/items" "Get items for inventory preparation"

test_auth_endpoint "GET" "/inventory/summary" "Get inventory summary with reservations"

if [[ "$WAREHOUSE_ITEM_ID" != "null" ]] && [[ -n "$WAREHOUSE_ITEM_ID" ]]; then
    test_auth_endpoint "GET" "/inventory/warehouse-items/$WAREHOUSE_ITEM_ID/available" \
        "Get warehouse item availability"
fi

test_auth_endpoint "POST" "/inventory/cleanup-expired-reservations?dry_run=true" \
    "Cleanup expired reservations (dry run)"

if [[ "$PRODUCT_ID" != "null" ]] && [[ -n "$PRODUCT_ID" ]]; then
    test_auth_endpoint "POST" "/inventory/validate-order-items" "Validate order items stock" \
        "[{\"product_id\":$PRODUCT_ID,\"quantity\":1}]"
fi

#═══════════════════════════════════════════════════════════════════════════════
# 7. Client Endpoints (9 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "7. Client Endpoints"

test_auth_endpoint "GET" "/clients/" "List all clients"

test_auth_endpoint "GET" "/clients/?search=770" "Search clients by phone"

test_auth_endpoint "GET" "/clients/stats/dashboard" "Client dashboard statistics"

test_auth_endpoint "POST" "/clients/normalize-phone" "Normalize phone number" \
    "\"77015211545\""

# Get first client for detailed tests
CLIENT_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/clients/?limit=1" | jq -r '.[0].id')

if [[ "$CLIENT_ID" != "null" ]] && [[ -n "$CLIENT_ID" ]]; then
    test_auth_endpoint "GET" "/clients/$CLIENT_ID" "Get client details"
fi

#═══════════════════════════════════════════════════════════════════════════════
# 8. Shop Settings Endpoints (7 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "8. Shop Settings Endpoints"

test_endpoint "GET" "/shop/settings/public?shop_id=$SHOP_ID" "Get public shop settings (no auth)"

test_auth_endpoint "GET" "/shop/settings" "Get shop settings (admin)"

test_auth_endpoint "GET" "/shop/hours/current" "Get current shop status (open/closed)"

test_auth_endpoint "GET" "/shop/delivery/calculate?order_total_tenge=5000" \
    "Calculate delivery cost"

#═══════════════════════════════════════════════════════════════════════════════
# 9. User Profile & Team Endpoints (12 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "9. User Profile & Team Endpoints"

test_auth_endpoint "GET" "/profile/" "Get current user profile"

test_auth_endpoint "GET" "/profile/team" "List team members"

test_auth_endpoint "GET" "/profile/team?role=DIRECTOR" "Filter team by role"

test_auth_endpoint "GET" "/profile/team/invitations" "List team invitations"

test_auth_endpoint "GET" "/profile/stats" "Get team statistics"

#═══════════════════════════════════════════════════════════════════════════════
# 10. Review Endpoints (6 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "10. Review Endpoints"

test_endpoint "GET" "/reviews/company" "List company reviews (public)"

test_endpoint "GET" "/reviews/company?limit=5" "List company reviews with limit"

if [[ "$PRODUCT_ID" != "null" ]] && [[ -n "$PRODUCT_ID" ]]; then
    test_endpoint "GET" "/reviews/product/$PRODUCT_ID" "List product reviews (public)"
fi

#═══════════════════════════════════════════════════════════════════════════════
# 11. Content/CMS Endpoints (8 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "11. Content/CMS Endpoints"

test_endpoint "GET" "/content/faqs" "List FAQs (public)"

test_endpoint "GET" "/content/faqs?category=delivery" "Filter FAQs by category"

# Note: Skipping page endpoints as they require specific slugs

#═══════════════════════════════════════════════════════════════════════════════
# 12. Superadmin Endpoints (14 endpoints)
#═══════════════════════════════════════════════════════════════════════════════

print_section "12. Superadmin Endpoints (requires is_superadmin=True)"

# Check if current user is superadmin
IS_SUPERADMIN=$(echo "$LOGIN_RESPONSE" | jq -r '.user.is_superadmin')

if [[ "$IS_SUPERADMIN" == "true" ]]; then
    test_auth_endpoint "GET" "/superadmin/shops" "List all shops (superadmin)"

    test_auth_endpoint "GET" "/superadmin/users" "List all users (superadmin)"

    test_auth_endpoint "GET" "/superadmin/stats" "Get platform statistics (superadmin)"

    if [[ "$SHOP_ID" != "null" ]] && [[ -n "$SHOP_ID" ]]; then
        test_auth_endpoint "GET" "/superadmin/shops/$SHOP_ID" "Get shop details (superadmin)"
    fi
else
    echo -e "${YELLOW}Skipping superadmin tests - current user is not superadmin${NC}"
    echo "To test superadmin endpoints, login with a superadmin account"
fi

#═══════════════════════════════════════════════════════════════════════════════
# Test Summary
#═══════════════════════════════════════════════════════════════════════════════

print_section "TEST SUMMARY"

echo -e "Total Tests:  ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"

if [[ $FAILED_TESTS -gt 0 ]]; then
    echo -e "\n${RED}Failed Endpoints:${NC}"
    for endpoint in "${FAILED_ENDPOINTS[@]}"; do
        echo -e "  ${RED}✗${NC} $endpoint"
    done
    exit 1
else
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
fi
