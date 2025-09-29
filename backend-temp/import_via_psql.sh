#!/bin/bash

# Render PostgreSQL External URL
# You need to get this from Render Dashboard
echo "⚠️  ВАЖНО: Для импорта данных в Render PostgreSQL:"
echo ""
echo "1. Откройте Render Dashboard: https://dashboard.render.com"
echo "2. Нажмите на вашу базу данных: figma-catalog-db"
echo "3. Найдите 'External Database URL' (не Internal!)"
echo "4. Скопируйте URL и выполните команду:"
echo ""
echo "export DATABASE_URL='ваш_external_url_здесь'"
echo "psql \$DATABASE_URL < /Users/alekenov/figma-product-catalog/backend/postgres_data.sql"
echo ""
echo "Или используйте команду с паролем:"
echo "PGPASSWORD='ваш_пароль' psql -h dpg-d3d3i07diees738dl92g-a.oregon-postgres.render.com -U figma_catalog_db_user -d figma_catalog_db -p 5432 < /Users/alekenov/figma-product-catalog/backend/postgres_data.sql"
echo ""
echo "Примечание: External URL уже содержит SSL параметры для подключения извне."