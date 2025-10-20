#!/bin/bash

# Скрипт для проверки MCP tool calls в логах AI Agent
echo "=== Проверка MCP Tool Calls ==="
echo ""
echo "Ожидание новых логов (15 секунд)..."
sleep 15

echo ""
echo "=== Последние tool calls в AI Agent ==="
railway logs --tail 200 2>&1 | grep -E "tool_call|tool_result|get_client_profile|list_products|create_order|kaspi" | tail -50

echo ""
echo "=== Полный контекст последнего запроса ==="
railway logs --tail 200 2>&1 | grep -B 5 -A 10 "1 букет\|счет выстави" | tail -40
