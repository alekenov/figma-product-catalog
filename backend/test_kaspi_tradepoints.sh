#!/bin/bash
#
# Kaspi Trade Points API Tester - Bash/cURL version
#
# Тестирует получение списка торговых точек через Kaspi QR API
# с использованием mTLS (mutual TLS) аутентификации.
#
# Использование:
#   ./test_kaspi_tradepoints.sh [BIN] [env]
#
# Примеры:
#   ./test_kaspi_tradepoints.sh                    # test env, default BIN
#   ./test_kaspi_tradepoints.sh 991011000048       # test env, custom BIN
#   ./test_kaspi_tradepoints.sh 991011000048 prod  # prod env, custom BIN
#

set -e  # Exit on error

# ==================== Configuration ====================

# Default values
BIN="${1:-991011000048}"
ENV="${2:-test}"
CERT_PATH="/home/bitrix/kaspi_certificates/prod/cvety.cer"
KEY_PATH="/home/bitrix/kaspi_certificates/prod/cvety-new.key"
KEY_PASSWORD="sy3t6G2HhuG1m4pEK8AJ2"

# API endpoints
if [ "$ENV" = "prod" ]; then
    BASE_URL="https://mtoke.kaspi.kz:8545"
else
    BASE_URL="https://mtokentest.kaspi.kz:8545"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== Helper Functions ====================

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ==================== Check Prerequisites ====================

check_prerequisites() {
    print_header "Проверка окружения"

    # Check curl
    if ! command -v curl &> /dev/null; then
        print_error "curl не установлен"
        exit 1
    fi
    print_info "curl: $(curl --version | head -n1)"

    # Check jq (optional but recommended)
    if command -v jq &> /dev/null; then
        print_info "jq: $(jq --version)"
        HAS_JQ=1
    else
        print_warning "jq не установлен - JSON форматирование недоступно"
        HAS_JQ=0
    fi

    # Check certificates
    if [ ! -f "$CERT_PATH" ]; then
        print_error "Сертификат не найден: $CERT_PATH"
        exit 1
    fi
    print_info "Сертификат: $CERT_PATH ($(stat -f%z "$CERT_PATH" 2>/dev/null || stat -c%s "$CERT_PATH") bytes)"

    if [ ! -f "$KEY_PATH" ]; then
        print_error "Ключ не найден: $KEY_PATH"
        exit 1
    fi
    print_info "Ключ: $KEY_PATH ($(stat -f%z "$KEY_PATH" 2>/dev/null || stat -c%s "$KEY_PATH") bytes)"

    echo ""
}

# ==================== Main Test Function ====================

test_trade_points() {
    print_header "Запрос торговых точек - Kaspi QR API"

    echo "Environment: $ENV"
    echo "Base URL: $BASE_URL"
    echo "БИН организации: $BIN"
    echo "Request-ID: $(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)"
    echo ""

    local url="${BASE_URL}/r3/v01/partner/tradepoints/${BIN}"

    print_info "Выполняем запрос..."
    echo "URL: $url"
    echo ""

    # ВАЖНО: curl поддерживает пароли для ключей через --pass опцию
    # Но это работает только если OpenSSL был собран с поддержкой password callbacks

    # Запрос с подробным выводом
    local response
    local http_code
    local temp_file=$(mktemp)

    # Выполняем curl с сохранением response и http_code
    http_code=$(curl -w "%{http_code}" -o "$temp_file" \
        --request GET \
        --url "$url" \
        --cert "$CERT_PATH" \
        --key "$KEY_PATH":"$KEY_PASSWORD" \
        --header "X-Request-ID: $(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)" \
        --header "Content-Type: application/json" \
        --verbose \
        --insecure \
        2>&1 | tee /tmp/kaspi_curl_debug.log | grep "^< HTTP" | tail -1 | awk '{print $3}')

    response=$(cat "$temp_file")
    rm -f "$temp_file"

    echo ""
    print_header "Response"
    echo "HTTP Status Code: $http_code"
    echo ""

    # Parse and display response
    if [ $HAS_JQ -eq 1 ]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo "$response"
    fi

    # Parse status code from JSON
    local status_code
    if [ $HAS_JQ -eq 1 ]; then
        status_code=$(echo "$response" | jq -r '.StatusCode // "unknown"' 2>/dev/null)
    else
        status_code=$(echo "$response" | grep -o '"StatusCode":[0-9-]*' | cut -d: -f2)
    fi

    echo ""
    print_header "Результат"

    # Check result
    if [ "$status_code" = "0" ]; then
        print_success "Запрос выполнен успешно!"

        # Extract trade points
        if [ $HAS_JQ -eq 1 ]; then
            local trade_points=$(echo "$response" | jq -r '.Data[] | "  - ID: \(.TradePointId), Название: \(.TradePointName)"' 2>/dev/null)
            if [ -n "$trade_points" ]; then
                echo ""
                echo "Торговые точки:"
                echo "$trade_points"
            fi
        fi

    else
        print_error "Ошибка при запросе торговых точек"
        echo "StatusCode: $status_code"

        # Error hints
        case "$status_code" in
            -10000)
                print_warning "Ошибка авторизации - проверьте:"
                echo "  1. Сертификат и ключ корректны"
                echo "  2. IP адрес сервера в whitelist у Kaspi"
                echo "  3. Пароль ключа правильный"
                ;;
            -999)
                print_warning "Техническая ошибка Kaspi API"
                ;;
            -14000002)
                print_warning "Торговые точки не найдены для БИНа $BIN"
                ;;
        esac
    fi

    echo ""
    print_info "Debug лог сохранен в: /tmp/kaspi_curl_debug.log"
    echo ""
}

# ==================== Device Registration ====================

register_device() {
    local trade_point_id="$1"
    local device_id="${2:-cvety-railway-test-001}"

    print_header "Регистрация устройства"

    local url="${BASE_URL}/r3/v01/device/register"

    local payload="{
        \"OrganizationBin\": \"$BIN\",
        \"DeviceId\": \"$device_id\",
        \"TradePointId\": $trade_point_id
    }"

    print_info "Регистрируем устройство на торговой точке $trade_point_id..."
    echo "Device ID: $device_id"
    echo ""

    local temp_file=$(mktemp)

    curl -w "\n" -o "$temp_file" \
        --request POST \
        --url "$url" \
        --cert "$CERT_PATH" \
        --key "$KEY_PATH":"$KEY_PASSWORD" \
        --header "X-Request-ID: $(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)" \
        --header "Content-Type: application/json" \
        --data "$payload" \
        --verbose \
        --insecure \
        2>&1 | tee /tmp/kaspi_register_debug.log

    local response=$(cat "$temp_file")
    rm -f "$temp_file"

    echo ""
    print_header "Response"

    if [ $HAS_JQ -eq 1 ]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo "$response"
    fi

    # Extract DeviceToken
    local device_token
    if [ $HAS_JQ -eq 1 ]; then
        device_token=$(echo "$response" | jq -r '.Data.DeviceToken // empty' 2>/dev/null)
    else
        device_token=$(echo "$response" | grep -o '"DeviceToken":"[^"]*"' | cut -d'"' -f4)
    fi

    if [ -n "$device_token" ]; then
        echo ""
        print_success "Устройство зарегистрировано!"
        echo "DeviceToken: $device_token"
        echo ""
        print_info "Сохраните в таблице KaspiPayConfig:"
        echo "  organization_bin: $BIN"
        echo "  trade_point_id: $trade_point_id"
        echo "  device_token: $device_token"
    else
        print_error "Не удалось зарегистрировать устройство"
    fi

    echo ""
}

# ==================== Main Script ====================

main() {
    print_header "Kaspi Trade Points API Tester"
    echo "БИН: $BIN"
    echo "Environment: $ENV"
    echo ""

    check_prerequisites
    test_trade_points

    # Uncomment to test device registration:
    # register_device 1 "cvety-railway-test-001"
}

main
