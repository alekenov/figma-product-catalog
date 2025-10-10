#!/usr/bin/env python3
"""
Direct testing of admin MCP tools.

This script bypasses the AI conversation layer and directly tests admin MCP tools
to ensure they work correctly with proper authentication.

Tests:
- create_product
- update_product
- list_orders
- get_order
- list_warehouse_items
- add_warehouse_stock
- update_shop_settings
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from pathlib import Path

class MCPAdminToolTester:
    """Direct tester for admin MCP tools."""

    def __init__(self):
        self.mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        self.backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")
        self.shop_id = int(os.getenv("SHOP_ID", "8"))
        self.token = None
        self.test_results = []

    async def login(self):
        """Login to get JWT token for admin operations."""
        print("🔐 Logging in...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_url}/call-tool",
                json={
                    "name": "login",
                    "arguments": {
                        "phone": "77015211545",
                        "password": "password"
                    }
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                # HTTP server format: {"result": {...}}
                if "result" in result:
                    data = result["result"]
                    self.token = data.get("access_token")
                    print(f"✅ Logged in successfully (token: {self.token[:20]}...)")
                    return True

            print(f"❌ Login failed: {response.text}")
            return False

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call an MCP tool and return the result."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_url}/call-tool",
                json={
                    "name": tool_name,
                    "arguments": arguments
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                # HTTP server format: {"result": {...}}
                return result.get("result", result)
            else:
                raise Exception(f"Tool call failed: {response.text}")

    def record_result(self, tool_name: str, success: bool, duration_ms: float, details: str = ""):
        """Record test result."""
        self.test_results.append({
            "tool": tool_name,
            "success": success,
            "duration_ms": duration_ms,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        status = "✅" if success else "❌"
        print(f"{status} {tool_name} ({duration_ms:.0f}ms) - {details}")

    async def test_create_product(self):
        """Test create_product tool."""
        print("\n📦 Testing create_product...")
        start = datetime.now()

        try:
            result = await self.call_tool("create_product", {
                "token": self.token,
                "name": f"[TEST] Букет тестовый {datetime.now().strftime('%H:%M:%S')}",
                "type": "flowers",
                "price": 9900000,  # 99,000 tenge in tiyins
                "description": "Автоматический тест создания товара",
                "enabled": False  # Disabled so it doesn't appear in catalog
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly
            if result and isinstance(result, dict):
                product_id = result.get("id")
                self.record_result("create_product", True, duration, f"Product ID: {product_id}")
                return product_id
            else:
                self.record_result("create_product", False, duration, "No valid response")
                return None

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("create_product", False, duration, str(e))
            return None

    async def test_update_product(self, product_id: int):
        """Test update_product tool."""
        print("\n📝 Testing update_product...")
        start = datetime.now()

        try:
            result = await self.call_tool("update_product", {
                "token": self.token,
                "product_id": product_id,
                "price": 10500000,  # Update price to 105,000 tenge
                "description": "Обновлено через автоматический тест"
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly
            if result and isinstance(result, dict):
                updated_price = result.get("price")
                self.record_result("update_product", True, duration, f"Updated price: {updated_price}")
            else:
                self.record_result("update_product", False, duration, "No valid response")

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("update_product", False, duration, str(e))

    async def test_list_orders(self):
        """Test list_orders tool."""
        print("\n📋 Testing list_orders...")
        start = datetime.now()

        try:
            result = await self.call_tool("list_orders", {
                "token": self.token,
                "limit": 5
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly (can be empty list)
            if isinstance(result, list):
                order_count = len(result)
                self.record_result("list_orders", True, duration, f"Found {order_count} orders")
                return result[0]["id"] if order_count > 0 else None
            else:
                self.record_result("list_orders", False, duration, "No valid response")
                return None

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("list_orders", False, duration, str(e))
            return None

    async def test_get_order(self, order_id: int):
        """Test get_order tool."""
        print("\n🔍 Testing get_order...")
        start = datetime.now()

        try:
            result = await self.call_tool("get_order", {
                "token": self.token,
                "order_id": order_id
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly
            if result and isinstance(result, dict):
                order_number = result.get("orderNumber")
                self.record_result("get_order", True, duration, f"Order: {order_number}")
            else:
                self.record_result("get_order", False, duration, "No valid response")

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("get_order", False, duration, str(e))

    async def test_list_warehouse_items(self):
        """Test list_warehouse_items tool."""
        print("\n📦 Testing list_warehouse_items...")
        start = datetime.now()

        try:
            result = await self.call_tool("list_warehouse_items", {
                "token": self.token,
                "limit": 10
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly (can be empty list)
            if isinstance(result, list):
                item_count = len(result)
                self.record_result("list_warehouse_items", True, duration, f"Found {item_count} items")
                return result[0]["id"] if item_count > 0 else None
            else:
                self.record_result("list_warehouse_items", False, duration, "No valid response")
                return None

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("list_warehouse_items", False, duration, str(e))
            return None

    async def test_add_warehouse_stock(self, warehouse_item_id: int):
        """Test add_warehouse_stock tool."""
        print("\n➕ Testing add_warehouse_stock...")
        start = datetime.now()

        try:
            result = await self.call_tool("add_warehouse_stock", {
                "token": self.token,
                "warehouse_item_id": warehouse_item_id,
                "quantity": 5,
                "notes": "Автоматический тест добавления количества"
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly
            if result and isinstance(result, dict):
                balance_after = result.get("balance_after")
                self.record_result("add_warehouse_stock", True, duration, f"Balance after: {balance_after}")
            else:
                self.record_result("add_warehouse_stock", False, duration, "No valid response")

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("add_warehouse_stock", False, duration, str(e))

    async def test_update_shop_settings(self):
        """Test update_shop_settings tool."""
        print("\n⚙️  Testing update_shop_settings...")
        start = datetime.now()

        try:
            result = await self.call_tool("update_shop_settings", {
                "token": self.token,
                "description": f"Тест обновлен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            })

            duration = (datetime.now() - start).total_seconds() * 1000

            # HTTP server returns data directly
            if result and isinstance(result, dict):
                shop_name = result.get("shop_name")
                self.record_result("update_shop_settings", True, duration, f"Shop: {shop_name}")
            else:
                self.record_result("update_shop_settings", False, duration, "No valid response")

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            self.record_result("update_shop_settings", False, duration, str(e))

    async def run_all_tests(self):
        """Run all admin tool tests."""
        print("="  * 60)
        print("🧪 ADMIN MCP TOOLS TEST SUITE")
        print("=" * 60)

        # Login first
        if not await self.login():
            print("❌ Cannot continue without authentication")
            return

        # Test product management
        product_id = await self.test_create_product()
        if product_id:
            await self.test_update_product(product_id)

        # Test order management
        order_id = await self.test_list_orders()
        if order_id:
            await self.test_get_order(order_id)

        # Test warehouse management
        warehouse_item_id = await self.test_list_warehouse_items()
        if warehouse_item_id:
            await self.test_add_warehouse_stock(warehouse_item_id)

        # Test shop settings
        await self.test_update_shop_settings()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed

        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")

        # Save detailed results
        report_dir = Path("reports") / f"admin_tools_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        report_dir.mkdir(parents=True, exist_ok=True)

        with open(report_dir / "results.json", "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": (passed/total)*100
                },
                "tests": self.test_results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n📁 Detailed results saved to: {report_dir}/results.json")

        return passed == total


async def main():
    """Main entry point."""
    tester = MCPAdminToolTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
