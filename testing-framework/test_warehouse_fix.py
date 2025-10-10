import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        # Login
        login_resp = await client.post(
            "http://localhost:8000/call-tool",
            json={"name": "login", "arguments": {"phone": "77015211545", "password": "password"}}
        )
        token = login_resp.json()["result"]["access_token"]
        print(f"✅ Logged in, token: {token[:20]}...")
        
        # List warehouse items
        list_resp = await client.post(
            "http://localhost:8000/call-tool",
            json={"name": "list_warehouse_items", "arguments": {"token": token, "limit": 5}}
        )
        items = list_resp.json()["result"]
        print(f"\n📦 Found {len(items)} warehouse items")
        
        if len(items) == 0:
            print("⚠️  No warehouse items to test with - creating one...")
            # Create warehouse item for testing
            create_resp = await httpx.AsyncClient().post(
                "http://localhost:8014/api/v1/warehouse/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "name": "Test Item for MCP",
                    "quantity": 10,
                    "cost_price": 50000,  # 500 tenge
                    "retail_price": 100000  # 1000 tenge
                }
            )
            if create_resp.status_code == 200:
                item_id = create_resp.json()["id"]
                print(f"✅ Created test item ID: {item_id}")
            else:
                print(f"❌ Failed to create item: {create_resp.status_code}")
                print(create_resp.text)
                return
        else:
            item_id = items[0]["id"]
            print(f"Using existing item ID: {item_id}")
        
        # Test add_warehouse_stock
        print(f"\n➕ Testing add_warehouse_stock for item {item_id}...")
        stock_resp = await client.post(
            "http://localhost:8000/call-tool",
            json={
                "name": "add_warehouse_stock",
                "arguments": {
                    "token": token,
                    "warehouse_item_id": item_id,
                    "quantity": 5,
                    "notes": "Тест после исправления"
                }
            }
        )
        
        if stock_resp.status_code == 200:
            result = stock_resp.json()["result"]
            print(f"✅ add_warehouse_stock SUCCESS!")
            print(f"   Balance after: {result.get('balance_after')}")
            print(f"   Quantity change: {result.get('quantity_change')}")
        else:
            print(f"❌ add_warehouse_stock FAILED: {stock_resp.status_code}")
            print(stock_resp.text)

asyncio.run(test())
