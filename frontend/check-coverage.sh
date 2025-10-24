#!/bin/bash
# Подсчет тестового покрытия

# Всего компонентов в src
total_components=$(find src -name "*.jsx" -not -name "*.test.jsx" -not -path "*/node_modules/*" | wc -l)

# Компонентов с тестами
tested_components=$(find src -name "*.test.jsx" | wc -l)

# Вычисляем процент
if [ $total_components -gt 0 ]; then
  coverage=$(echo "scale=2; ($tested_components * 100) / $total_components" | bc)
else
  coverage=0
fi

echo "📊 Тестовое покрытие компонентов:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Всего компонентов: $total_components"
echo "С тестами: $tested_components"
echo "Покрытие: ${coverage}%"
echo ""
echo "📝 Компоненты БЕЗ тестов:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Находим компоненты без тестов
for file in $(find src -name "*.jsx" -not -name "*.test.jsx" -not -path "*/node_modules/*"); do
  basename=$(basename "$file" .jsx)
  dir=$(dirname "$file")
  
  # Проверяем есть ли тест
  if [ ! -f "${dir}/${basename}.test.jsx" ]; then
    echo "❌ ${file#src/}"
  fi
done | head -20
