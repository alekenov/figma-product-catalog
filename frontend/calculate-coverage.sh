#!/bin/bash
echo "📊 Обновленное тестовое покрытие:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Всего файлов
total_js_files=$(find src -name "*.jsx" -o -name "*.js" | grep -v ".test." | grep -v "node_modules" | wc -l)
total_components=$(find src -name "*.jsx" | grep -v ".test." | grep -v "node_modules" | wc -l)

# С тестами
test_files=$(find src -name "*.test.jsx" -o -name "*.test.js" | wc -l)

echo "Всего компонентов (.jsx): $total_components"
echo "Всего файлов (.js + .jsx): $total_js_files"
echo "Тестовых файлов: $test_files"

# Процент
component_coverage=$(echo "scale=2; ($test_files * 100) / $total_components" | bc)
echo ""
echo "📈 Покрытие компонентов: ${component_coverage}%"

echo ""
echo "✅ Новые тесты для рефакторенных компонентов:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ls -1 src/components/profile/*.test.jsx src/components/profile/hooks/*.test.js src/components/orders/hooks/*.test.js 2>/dev/null | while read f; do
  tests=$(grep -c "it(" "$f" || echo "0")
  echo "  ✓ $(basename $f) - $tests тестов"
done

echo ""
echo "🎯 Прогресс к 80% покрытию:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
target=80
current=$component_coverage
need=$(echo "scale=0; ($total_components * $target / 100) - $test_files" | bc)
echo "Текущее: ${current}%"
echo "Цель: ${target}%"
if [ $need -gt 0 ]; then
  echo "Нужно еще тестов: ~$need файлов"
else
  echo "✅ Цель достигнута!"
fi
