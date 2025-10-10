"""Test update_order functionality directly against backend API"""
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("Test: Update Order Direct Backend API")
        print("=" * 60)

        # Step 1: Login to get admin token
        print("\n🔐 Step 1: Logging in as admin...")
        login_resp = await client.post(
            "http://localhost:8014/api/v1/auth/login",
            json={
                "phone": "77015211545",
                "password": "password"
            }
        )

        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.status_code}")
            print(login_resp.text)
            return

        token = login_resp.json()["access_token"]
        print(f"✅ Logged in successfully")

        # Step 2: Get existing order (we know order ID 13 exists from previous test)
        order_id = 13
        print(f"\n📦 Step 2: Getting order {order_id}...")

        get_resp = await client.get(
            f"http://localhost:8014/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        if get_resp.status_code == 200:
            order = get_resp.json()
            print(f"✅ Order found:")
            print(f"   Tracking ID: {order.get('tracking_id')}")
            print(f"   Customer: {order.get('customerName')}")
            print(f"   Current address: {order.get('delivery_address')}")
            print(f"   Status: {order.get('status')}")
        else:
            print(f"⚠️  Order not found, will create a new test order...")
            # Create a new order if ID 13 doesn't exist
            create_resp = await client.post(
                "http://localhost:8014/api/v1/orders/public/create?shop_id=8",
                json={
                    "customerName": "Update Test Customer",
                    "phone": "77099999999",
                    "delivery_address": "Original Address",
                    "delivery_date": "2025-10-07T14:00:00",
                    "items": [{"product_id": 21, "quantity": 1}],
                    "check_availability": False
                }
            )
            if create_resp.status_code != 200:
                print(f"❌ Failed to create order: {create_resp.status_code}")
                return
            order = create_resp.json()
            order_id = order["id"]
            print(f"✅ Created new order ID: {order_id}")
            print(f"   Tracking ID: {order.get('tracking_id')}")

        # Step 3: Update the order (change delivery address)
        print(f"\n🔄 Step 3: Updating order {order_id}...")
        new_address = "ул. Сатпаева, дом 45, кв. 12 (UPDATED)"
        new_notes = "Пожалуйста, позвоните за 30 минут до доставки"

        update_resp = await client.put(
            f"http://localhost:8014/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "delivery_address": new_address,
                "notes": new_notes
            }
        )

        if update_resp.status_code != 200:
            print(f"❌ Failed to update order: {update_resp.status_code}")
            print(update_resp.text)
            return

        updated_order = update_resp.json()
        print(f"✅ Order updated successfully!")
        print(f"   New address: {updated_order.get('delivery_address')}")
        print(f"   New notes: {updated_order.get('notes')}")

        # Step 4: Verify the update by fetching again
        print(f"\n🔍 Step 4: Verifying update...")
        verify_resp = await client.get(
            f"http://localhost:8014/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        if verify_resp.status_code == 200:
            verified_order = verify_resp.json()
            print(f"✅ Order verified!")
            print(f"   Address: {verified_order.get('delivery_address')}")
            print(f"   Notes: {verified_order.get('notes')}")

            if verified_order.get('delivery_address') == new_address and verified_order.get('notes') == new_notes:
                print("\n" + "=" * 60)
                print("🎉 SUCCESS: Backend update_order API works correctly!")
                print(f"   Order ID: {order_id}")
                print(f"   Tracking ID: {verified_order.get('tracking_id')}")
                print("=" * 60)
            else:
                print("\n" + "=" * 60)
                print("⚠️  WARNING: Update not persisted correctly")
                print("=" * 60)

asyncio.run(test())
