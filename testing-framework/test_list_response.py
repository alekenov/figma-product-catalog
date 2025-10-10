import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        # Login first
        login_resp = await client.post(
            "http://localhost:8000/call-tool",
            json={"name": "login", "arguments": {"phone": "77015211545", "password": "password"}}
        )
        token = login_resp.json()["result"]["access_token"]
        
        # Test list_orders
        resp1 = await client.post(
            "http://localhost:8000/call-tool",
            json={"name": "list_orders", "arguments": {"token": token, "limit": 2}}
        )
        print("=== list_orders response ===")
        print(json.dumps(resp1.json(), indent=2))
        
        # Test list_warehouse_items
        resp2 = await client.post(
            "http://localhost:8000/call-tool",
            json={"name": "list_warehouse_items", "arguments": {"token": token, "limit": 2}}
        )
        print("\n=== list_warehouse_items response ===")
        print(json.dumps(resp2.json(), indent=2))

asyncio.run(test())
