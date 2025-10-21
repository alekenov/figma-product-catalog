#!/bin/bash

# Integration test: webhook → embedding → database
# Tests webhook with int values for price and dimensions

echo "🧪 Testing webhook integration with int values..."

curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/product-sync" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: cvety-webhook-2025-secure-key" \
  -d '{
    "event_type": "product.created",
    "product_data": {
      "id": 999888,
      "title": "Test Product - Integration Test",
      "price": 15000,
      "isAvailable": true,
      "image": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
      "images": ["https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png"],
      "catalogHeight": 70,
      "catalogWidth": 50,
      "type": "catalog",
      "colors": false,
      "createdAt": "2025-10-21T12:00:00+0500"
    }
  }'

echo ""
echo "✅ Webhook request sent"
