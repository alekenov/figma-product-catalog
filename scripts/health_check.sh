#!/bin/bash

###############################################################################
# Health Check Script for Flower Shop Bot Services
#
# Usage:
#   ./scripts/health_check.sh [environment]
#
# Arguments:
#   environment - "local" or "production" (default: local)
#
# Examples:
#   ./scripts/health_check.sh local        # Check local services
#   ./scripts/health_check.sh production   # Check Railway production
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Environment (default: local)
ENV="${1:-local}"

# Service URLs based on environment
if [ "$ENV" = "production" ]; then
    BACKEND_URL="https://figma-product-catalog-production.up.railway.app"
    AI_AGENT_URL="https://ai-agent-service-production-c331.up.railway.app"
    TELEGRAM_BOT_URL="https://telegram-bot-production-75a7.up.railway.app"
else
    BACKEND_URL="http://localhost:8014"
    AI_AGENT_URL="http://localhost:8002"
    TELEGRAM_BOT_URL="http://localhost:8080"
fi

echo -e "${BLUE}🏥 Starting Health Check for ${ENV} environment...${NC}\n"

# Track results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

###############################################################################
# Helper Functions
###############################################################################

check_http_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking $name... "

    # Make request and capture status code and response time
    response=$(curl -s -w "\n%{http_code}\n%{time_total}" -o /tmp/health_response.txt "$url" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -2 | head -1)
    response_time=$(echo "$response" | tail -1)
    body=$(cat /tmp/health_response.txt 2>/dev/null || echo "")

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC} (${response_time}s)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Status: $status_code)"
        echo -e "${YELLOW}   Response: ${body:0:100}${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

check_json_field() {
    local name="$1"
    local url="$2"
    local field="$3"
    local expected_pattern="$4"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking $name ($field)... "

    response=$(curl -s "$url" 2>/dev/null || echo "{}")
    value=$(echo "$response" | grep -o "\"$field\":\"[^\"]*\"" | cut -d'"' -f4 || echo "")

    if echo "$value" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ OK${NC} ($value)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected: $expected_pattern, Got: $value)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

check_telegram_webhook() {
    local token="$1"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking Telegram webhook... "

    if [ -z "$token" ]; then
        echo -e "${YELLOW}⚠️  SKIPPED${NC} (TELEGRAM_TOKEN not set)"
        return 0
    fi

    response=$(curl -s "https://api.telegram.org/bot${token}/getWebhookInfo")
    webhook_url=$(echo "$response" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    pending_updates=$(echo "$response" | grep -o '"pending_update_count":[0-9]*' | cut -d':' -f2)
    last_error_message=$(echo "$response" | grep -o '"last_error_message":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$webhook_url" ]; then
        echo -e "${RED}❌ FAILED${NC} (No webhook set)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi

    if [ -n "$last_error_message" ]; then
        echo -e "${YELLOW}⚠️  WARNING${NC} (Last error: $last_error_message)"
    else
        echo -e "${GREEN}✅ OK${NC} (Pending: $pending_updates)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi

    echo -e "   Webhook URL: $webhook_url"
    return 0
}

###############################################################################
# 1. Backend Service Health Checks
###############################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 Backend Service ($BACKEND_URL)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_http_endpoint "Backend /health" "$BACKEND_URL/health" 200
check_http_endpoint "Backend /api/v1/products" "$BACKEND_URL/api/v1/products/?shop_id=8&limit=1" 200
check_http_endpoint "Backend /api/v1/shop/settings" "$BACKEND_URL/api/v1/shop/settings?shop_id=8" 200

echo ""

###############################################################################
# 2. AI Agent Service Health Checks
###############################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🤖 AI Agent Service ($AI_AGENT_URL)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_http_endpoint "AI Agent /health" "$AI_AGENT_URL/health" 200
check_json_field "AI Agent status" "$AI_AGENT_URL/health" "status" "healthy"
check_http_endpoint "AI Agent /cache-stats" "$AI_AGENT_URL/cache-stats" 200

# Check cache hit rate
echo -n "Checking cache hit rate... "
cache_response=$(curl -s "$AI_AGENT_URL/cache-stats" 2>/dev/null || echo "{}")
cache_hit_rate=$(echo "$cache_response" | grep -o '"cache_hit_rate":[0-9.]*' | cut -d':' -f2)

if [ -n "$cache_hit_rate" ]; then
    if (( $(echo "$cache_hit_rate > 70" | bc -l) )); then
        echo -e "${GREEN}✅ OK${NC} (${cache_hit_rate}% - Good!)"
    elif (( $(echo "$cache_hit_rate > 0" | bc -l) )); then
        echo -e "${YELLOW}⚠️  WARNING${NC} (${cache_hit_rate}% - Should be >70%)"
    else
        echo -e "${BLUE}ℹ️  INFO${NC} (${cache_hit_rate}% - Cache warming up)"
    fi
else
    echo -e "${YELLOW}⚠️  FAILED${NC} (Could not retrieve cache hit rate)"
fi

echo ""

###############################################################################
# 3. Telegram Bot Service Health Checks
###############################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📱 Telegram Bot Service ($TELEGRAM_BOT_URL)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_http_endpoint "Telegram Bot /health" "$TELEGRAM_BOT_URL/health" 200
check_json_field "Telegram Bot status" "$TELEGRAM_BOT_URL/health" "status" "ok"

# Check Telegram webhook (production only)
if [ "$ENV" = "production" ] && [ -n "$TELEGRAM_TOKEN" ]; then
    check_telegram_webhook "$TELEGRAM_TOKEN"
else
    echo -e "${BLUE}ℹ️  Skipping webhook check (local mode or TELEGRAM_TOKEN not set)${NC}"
fi

echo ""

###############################################################################
# 4. Integration Tests
###############################################################################

if [ "$ENV" = "production" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔗 Integration Tests${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Test AI Agent can reach Backend
    echo -n "Testing AI Agent → Backend connectivity... "
    products_response=$(curl -s "$BACKEND_URL/api/v1/products/?shop_id=8&limit=1")
    product_count=$(echo "$products_response" | grep -o '"id":[0-9]*' | wc -l)

    if [ "$product_count" -gt 0 ]; then
        echo -e "${GREEN}✅ OK${NC} (Products accessible)"
    else
        echo -e "${RED}❌ FAILED${NC} (No products found)"
    fi

    # Test response time
    echo -n "Testing AI Agent response time... "
    start_time=$(date +%s.%N)
    curl -s -X POST "$AI_AGENT_URL/chat" \
        -H "Content-Type: application/json" \
        -d '{"message":"привет","user_id":"health_check_bot","channel":"test"}' \
        > /dev/null 2>&1
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc)

    if (( $(echo "$response_time < 15" | bc -l) )); then
        echo -e "${GREEN}✅ OK${NC} (${response_time}s)"
    else
        echo -e "${YELLOW}⚠️  SLOW${NC} (${response_time}s - should be <15s)"
    fi

    echo ""
fi

###############################################################################
# 5. Environment Variables Check (production only)
###############################################################################

if [ "$ENV" = "production" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔒 Environment Variables${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    echo -e "${YELLOW}⚠️  Run manually: railway variables --service SERVICE_NAME${NC}"
    echo -e "${YELLOW}    Check: TELEGRAM_TOKEN, CLAUDE_API_KEY, DATABASE_URL${NC}"
    echo ""
fi

###############################################################################
# Summary
###############################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Health Check Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "Environment: ${BLUE}$ENV${NC}"
echo -e "Total Checks: ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "\n${GREEN}✅ All checks passed! System is healthy.${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ Some checks failed. Please investigate.${NC}\n"

    # Show next steps
    echo -e "${YELLOW}🔧 Troubleshooting Steps:${NC}"
    echo -e "1. Check Railway logs: railway logs --service SERVICE_NAME"
    echo -e "2. Verify environment variables: railway variables --service SERVICE_NAME"
    echo -e "3. Restart services: railway service SERVICE_NAME && railway restart"
    echo -e "4. See DEPLOYMENT_CHECKLIST.md for detailed troubleshooting"
    echo ""

    exit 1
fi
