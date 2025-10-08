#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMyIsInBob25lIjoiKzc3MDE1MjExNTQ1Iiwicm9sZSI6IkRJUkVDVE9SIiwic2hvcF9pZCI6bnVsbCwiZXhwIjoxNzYwMzgyMjQ4fQ.mnHKo8WAWagex0HiULFFZXAnVAYq7iuzDqONpGa1Np0"

echo "========================================="
echo "Testing Superadmin Products Endpoints"
echo "========================================="

echo -e "\n=== Test 1: GET /superadmin/products (list all) ==="
curl -s -X GET "http://localhost:8014/api/v1/superadmin/products?limit=2" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -40

echo -e "\n=== Test 2: GET /superadmin/products (filter by shop_id=8) ==="
curl -s -X GET "http://localhost:8014/api/v1/superadmin/products?shop_id=8&limit=2" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo -e "\n=== Test 3: PUT /superadmin/products/1/toggle ==="
curl -s -X PUT "http://localhost:8014/api/v1/superadmin/products/1/toggle" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n=== Test 4: PUT /superadmin/products/1 (update product) ==="
curl -s -X PUT "http://localhost:8014/api/v1/superadmin/products/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price": 15000}' | python3 -m json.tool

echo -e "\n========================================="
echo "Testing Superadmin Orders Endpoints"
echo "========================================="

echo -e "\n=== Test 5: GET /superadmin/orders (list all) ==="
curl -s -X GET "http://localhost:8014/api/v1/superadmin/orders?limit=2" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -60

echo -e "\n=== Test 6: GET /superadmin/orders/{id} (order detail) ==="
curl -s -X GET "http://localhost:8014/api/v1/superadmin/orders/1" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -40

echo -e "\n=== Test 7: PUT /superadmin/orders/2/status (update status) ==="
curl -s -X PUT "http://localhost:8014/api/v1/superadmin/orders/2/status?new_status=ACCEPTED" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n=== Test 8: PUT /superadmin/orders/1/cancel (cancel order) ==="
curl -s -X PUT "http://localhost:8014/api/v1/superadmin/orders/1/cancel?reason=Test%20cancellation" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n========================================="
echo "All tests completed!"
echo "========================================="
