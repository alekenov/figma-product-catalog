import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # Login
        login_resp = await client.post(
            "http://localhost:8000/call-tool",
            json={"name": "login", "arguments": {"phone": "77015211545", "password": "password"}}
        )
        token = login_resp.json()["result"]["access_token"]
        print(f"✅ Logged in, token: {token[:20]}...")
        
        # Create warehouse item directly via backend
        print("\n📦 Creating test warehouse item...")
        create_resp = await client.post(
            "http://localhost:8014/api/v1/warehouse/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Item for MCP",
                "quantity": 10,
                "cost_price_tenge": 500,
                "retail_price_tenge": 1000,
                "min_quantity": 5
            }
        )
        
        if create_resp.status_code == 200:
            item_id = create_resp.json()["id"]
            print(f"✅ Created test item ID: {item_id}")
        else:
            print(f"❌ Failed to create item: {create_resp.status_code}")
            print(create_resp.text)
            return
        
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
                    "notes": "Тест после исправления 422"
                }
            }
        )
        
        if stock_resp.status_code == 200:
            result = stock_resp.json()["result"]
            print(f"✅ add_warehouse_stock SUCCESS!")
            print(f"   Balance after: {result.get('balance_after')}")
            print(f"   Quantity change: {result.get('quantity_change')}")
            print(f"   Description: {result.get('description')}")
        else:
            print(f"❌ add_warehouse_stock FAILED: {stock_resp.status_code}")
            print(stock_resp.text)
        
        # Cleanup - delete test item
        print(f"\n🗑️  Deleting test item {item_id}...")
        del_resp = await client.delete(
            f"http://localhost:8014/api/v1/warehouse/{item_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if del_resp.status_code == 200:
            print("✅ Test item deleted")
        else:
            print(f"⚠️  Could not delete item: {del_resp.status_code}")

asyncio.run(test())
