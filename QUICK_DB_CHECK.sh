#!/bin/bash
# 🗄️ Быстрая проверка БД - Telegram клиентов

DB_PATH="/Users/alekenov/figma-product-catalog/backend/figma_catalog.db"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  📊 Telegram Clients Database Quick Check              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Проверка 1: Общее количество клиентов
echo "1️⃣  ОБЩЕЕ КОЛИЧЕСТВО КЛИЕНТОВ:"
sqlite3 "$DB_PATH" "SELECT COUNT(*) as total FROM client WHERE shop_id = 8;"
echo ""

# Проверка 2: Авторизованные (с Telegram)
echo "2️⃣  АВТОРИЗОВАННЫЕ ЧЕРЕЗ TELEGRAM:"
sqlite3 "$DB_PATH" << 'EOF'
SELECT COUNT(*) as authorized FROM client
WHERE shop_id = 8 AND telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0;
EOF
echo ""

# Проверка 3: Не авторизованные
echo "3️⃣  НЕ АВТОРИЗОВАННЫЕ:"
sqlite3 "$DB_PATH" << 'EOF'
SELECT COUNT(*) as not_authorized FROM client
WHERE shop_id = 8 AND (telegram_user_id IS NULL OR LENGTH(telegram_user_id) = 0);
EOF
echo ""

# Проверка 4: Список всех авторизованных
echo "4️⃣  СПИСОК АВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sqlite3 "$DB_PATH" -header -column << 'EOF'
SELECT
  id,
  phone,
  customerName,
  telegram_user_id,
  telegram_username,
  created_at
FROM client
WHERE shop_id = 8 AND telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0
ORDER BY created_at DESC;
EOF
echo ""

# Проверка 5: Статистика
echo "5️⃣  СТАТИСТИКА ПО МАГАЗИНУ (shop_id=8):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sqlite3 "$DB_PATH" -header -column << 'EOF'
SELECT
  COUNT(*) as total_clients,
  COUNT(CASE WHEN telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0 THEN 1 END) as telegram_authorized,
  COUNT(CASE WHEN telegram_user_id IS NULL OR LENGTH(telegram_user_id) = 0 THEN 1 END) as not_authorized,
  ROUND(100.0 * COUNT(CASE WHEN telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0 THEN 1 END) / COUNT(*), 1) as auth_percentage
FROM client
WHERE shop_id = 8;
EOF
echo ""

# Проверка 6: Последние добавленные клиенты
echo "6️⃣  ПОСЛЕДНИЕ 5 ДОБАВЛЕННЫХ КЛИЕНТОВ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sqlite3 "$DB_PATH" -header -column << 'EOF'
SELECT
  id,
  phone,
  customerName,
  telegram_user_id,
  created_at
FROM client
WHERE shop_id = 8
ORDER BY created_at DESC
LIMIT 5;
EOF
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ Проверка завершена                                 ║"
echo "╚════════════════════════════════════════════════════════╝"
