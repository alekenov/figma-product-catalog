"""Test direct backend API call to debug 500 error"""
import httpx
import asyncio
from datetime import datetime, timedelta

async def test():
    async with httpx.AsyncClient() as client:
        # Test 1: Order without delivery_date
        print("Test 1: Creating order without delivery_date...")
        resp1 = await client.post(
            "http://localhost:8014/api/v1/orders/public/create?shop_id=8",
            json={
                "customerName": "Тест Клиент",
                "phone": "77012345678",
                "items": [{"product_id": 21, "quantity": 1}],
                "check_availability": False
            }
        )
        print(f"Status: {resp1.status_code}")
        print(f"Response: {resp1.text}\n")

        # Test 2: Order with delivery_date as datetime string
        print("Test 2: Creating order with delivery_date as ISO string...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT14:00:00")
        resp2 = await client.post(
            "http://localhost:8014/api/v1/orders/public/create?shop_id=8",
            json={
                "customerName": "Тест Клиент 2",
                "phone": "77012345679",
                "delivery_address": "ул. Абая, дом 10",
                "delivery_date": tomorrow,
                "items": [{"product_id": 21, "quantity": 1}],
                "check_availability": False
            }
        )
        print(f"Status: {resp2.status_code}")
        print(f"Response: {resp2.text}\n")

asyncio.run(test())
