#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_BASE="https://figma-product-catalog-production.up.railway.app/api/v1"
SHOP_ID=8
TEST_PHONE="77777777777"  # Тестовый номер

echo -e "${BLUE}=== Тест системы персонализации клиентов ===${NC}\n"

# Шаг 1: Получить токен (если есть)
echo -e "${YELLOW}Шаг 1: Попытка получить профиль (должен вернуть 404)${NC}"
curl -s "$API_BASE/client_profile?phone=$TEST_PHONE" \
  -H "shop_id: $SHOP_ID" | python3 -m json.tool
echo -e "\n"

# Шаг 2: Создать тестовый заказ
echo -e "${YELLOW}Шаг 2: Создание тестового заказа${NC}"
ORDER_RESPONSE=$(curl -s -X POST "$API_BASE/orders/public/create?shop_id=$SHOP_ID" \
  -H "Content-Type: application/json" \
  -d "{
    \"customerName\": \"$TEST_PHONE\",
    \"phone\": \"$TEST_PHONE\",
    \"delivery_address\": \"ул. Тестовая 123\",
    \"recipient_name\": \"Тестовый Получатель\",
    \"recipient_phone\": \"77888888888\",
    \"delivery_type\": \"delivery\",
    \"delivery_cost\": 150000,
    \"items\": [{\"product_id\": 3, \"quantity\": 1}],
    \"total_price\": 2000000,
    \"payment_method\": \"cash\",
    \"notes\": \"Тест персонализации\"
  }")

echo "$ORDER_RESPONSE" | python3 -m json.tool

# Извлечь order_id из ответа
ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order', {}).get('id', 'null'))")
echo -e "${GREEN}Создан заказ #$ORDER_ID${NC}\n"

# Шаг 3: Информация о следующих шагах
echo -e "${YELLOW}Шаг 3: Действия для тестирования${NC}"
echo "1. Откройте админку: https://frontend-production-6869.up.railway.app"
echo "2. Найдите заказ #$ORDER_ID"
echo "3. Переведите статус в: PAID -> ACCEPTED -> IN_PRODUCTION -> READY -> IN_DELIVERY -> DELIVERED"
echo "4. После статуса DELIVERED профиль автоматически создастся/обновится"
echo -e "\n"

# Шаг 4: Проверка профиля (вручную через некоторое время)
echo -e "${YELLOW}Шаг 4: Проверка профиля (запустите после перевода в DELIVERED)${NC}"
echo "curl -s \"$API_BASE/client_profile?phone=$TEST_PHONE\" -H \"shop_id: $SHOP_ID\" | python3 -m json.tool"
echo -e "\n"

# Шаг 5: GDPR тесты
echo -e "${YELLOW}Шаг 5: GDPR действия (опционально)${NC}"
echo "# Отключить персонализацию:"
echo "curl -X PATCH \"$API_BASE/client_profile/privacy?phone=$TEST_PHONE&action=disable_personalization\" -H \"shop_id: $SHOP_ID\""
echo ""
echo "# Включить обратно:"
echo "curl -X PATCH \"$API_BASE/client_profile/privacy?phone=$TEST_PHONE&action=enable_personalization\" -H \"shop_id: $SHOP_ID\""
echo ""
echo "# Удалить все данные:"
echo "curl -X PATCH \"$API_BASE/client_profile/privacy?phone=$TEST_PHONE&action=delete_profile_data\" -H \"shop_id: $SHOP_ID\""
echo -e "\n"

echo -e "${GREEN}=== Тест завершен! ===${NC}"
echo "Телефон для тестирования: $TEST_PHONE"
echo "ID заказа: $ORDER_ID"
