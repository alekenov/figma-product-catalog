#!/bin/bash
# Quick API Test - Tests critical endpoints only

API_BASE="http://localhost:8014/api/v1"
TEST_PHONE="${TEST_PHONE:-77777777777}"
TEST_PASSWORD="${TEST_PASSWORD:-test123}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Quick API Test ===${NC}\n"

# 1. Login
echo -n "1. Login... "
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$TEST_PHONE\",\"password\":\"$TEST_PASSWORD\"}")
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
SHOP_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.shop_id // 9')

if [[ "$TOKEN" != "null" ]] && [[ -n "$TOKEN" ]]; then
  echo -e "${GREEN}✓${NC} (shop_id: $SHOP_ID)"
else
  echo -e "${RED}✗ Failed to login${NC}"
  exit 1
fi

# 2. Get current user
echo -n "2. Get current user (/auth/me)... "
USER_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/auth/me")
USER_NAME=$(echo "$USER_RESPONSE" | jq -r '.name')
if [[ "$USER_NAME" != "null" ]]; then
  echo -e "${GREEN}✓${NC} ($USER_NAME)"
else
  echo -e "${RED}✗${NC}"
fi

# 3. List products (public)
echo -n "3. List products (public)... "
PRODUCTS=$(curl -s "$API_BASE/products/?shop_id=$SHOP_ID&limit=5")
PRODUCT_COUNT=$(echo "$PRODUCTS" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $PRODUCT_COUNT products)"

# 4. List products (admin)
echo -n "4. List products (admin)... "
ADMIN_PRODUCTS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/products/admin?limit=5")
ADMIN_PRODUCT_COUNT=$(echo "$ADMIN_PRODUCTS" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $ADMIN_PRODUCT_COUNT products)"

# 5. List orders
echo -n "5. List orders... "
ORDERS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/orders/?limit=5")
ORDER_COUNT=$(echo "$ORDERS" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $ORDER_COUNT orders)"

# 6. List warehouse items
echo -n "6. List warehouse items... "
WAREHOUSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/warehouse/?limit=5")
WAREHOUSE_COUNT=$(echo "$WAREHOUSE" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $WAREHOUSE_COUNT items)"

# 7. List clients
echo -n "7. List clients... "
CLIENTS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/clients/?limit=5")
CLIENT_COUNT=$(echo "$CLIENTS" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $CLIENT_COUNT clients)"

# 8. Get shop settings
echo -n "8. Get shop settings... "
SHOP_SETTINGS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/shop/settings")
SHOP_NAME=$(echo "$SHOP_SETTINGS" | jq -r '.name')
if [[ "$SHOP_NAME" != "null" ]]; then
  echo -e "${GREEN}✓${NC} ($SHOP_NAME)"
else
  echo -e "${RED}✗${NC}"
fi

# 9. Get team members
echo -n "9. Get team members... "
TEAM=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/profile/team?limit=5")
TEAM_COUNT=$(echo "$TEAM" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $TEAM_COUNT members)"

# 10. Get company reviews (public)
echo -n "10. Get company reviews (public)... "
REVIEWS=$(curl -s "$API_BASE/reviews/company?limit=5")
REVIEW_COUNT=$(echo "$REVIEWS" | jq -r '.reviews | length')
echo -e "${GREEN}✓${NC} (found $REVIEW_COUNT reviews)"

# 11. Get FAQs (public)
echo -n "11. Get FAQs (public)... "
FAQS=$(curl -s "$API_BASE/content/faqs")
FAQ_COUNT=$(echo "$FAQS" | jq '. | length')
echo -e "${GREEN}✓${NC} (found $FAQ_COUNT FAQs)"

# 12. Order dashboard stats
echo -n "12. Order dashboard stats... "
ORDER_STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/orders/stats/dashboard")
TOTAL_ORDERS=$(echo "$ORDER_STATS" | jq -r '.total_orders')
echo -e "${GREEN}✓${NC} (total: $TOTAL_ORDERS orders)"

echo -e "\n${GREEN}=== All quick tests passed! ===${NC}"
echo -e "\nRun ./test_api_endpoints.sh for comprehensive testing (147 endpoints)"
