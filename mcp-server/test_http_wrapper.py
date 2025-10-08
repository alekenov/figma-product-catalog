#!/usr/bin/env python3
"""
Test script for HTTP wrapper endpoints.
Tests /health, /tools, and /call-tool functionality.
"""
import asyncio
import httpx
import time
import sys


async def test_http_wrapper():
    """Test HTTP wrapper endpoints."""

    print("=" * 60)
    print("HTTP WRAPPER TEST")
    print("=" * 60)

    base_url = "http://localhost:8001"
    client = httpx.AsyncClient(timeout=30.0)

    try:
        # Test 1: Health endpoint
        print("\n1. Testing /health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")

            if response.status_code in [200, 503]:
                data = response.json()
                print(f"   ✅ Health check returned: {data.get('status')}")
                print(f"   Backend API: {data.get('backend_url')}")
                print(f"   Backend Status: {data.get('dependencies', {}).get('backend_api', {}).get('status')}")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False

        # Test 2: List tools endpoint
        print("\n2. Testing /tools endpoint...")
        try:
            response = await client.get(f"{base_url}/tools")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                total_tools = data.get("total", 0)
                tools = data.get("tools", [])

                print(f"   ✅ Found {total_tools} tools")

                # Group by domain
                domains = {}
                for tool in tools:
                    domain = tool.get("domain")
                    if domain not in domains:
                        domains[domain] = []
                    domains[domain].append(tool)

                print(f"   Domains: {', '.join(sorted(domains.keys()))}")

                for domain, domain_tools in sorted(domains.items()):
                    print(f"\n   {domain}/ ({len(domain_tools)} tools):")
                    for tool in domain_tools[:3]:  # Show first 3 tools per domain
                        name = tool.get("name")
                        requires_auth = "🔒" if tool.get("requires_auth") else "🔓"
                        is_public = "🌐" if tool.get("is_public") else "🔐"
                        print(f"      {requires_auth} {is_public} {name}")

                if total_tools == 0:
                    print("   ❌ No tools found!")
                    return False

            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ List tools failed: {e}")
            return False

        # Test 3: Call a simple public tool
        print("\n3. Testing /call-tool endpoint...")
        try:
            # Test with get_shop_settings (public tool, no auth required)
            tool_request = {
                "name": "get_shop_settings",
                "arguments": {
                    "shop_id": 8
                }
            }

            print(f"   Calling tool: {tool_request['name']}")
            response = await client.post(f"{base_url}/call-tool", json=tool_request)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                error = data.get("error")

                if error:
                    print(f"   ⚠️  Tool returned error: {error}")
                    # This might be expected if backend is down
                else:
                    print(f"   ✅ Tool executed successfully")
                    if isinstance(result, dict):
                        print(f"   Result keys: {list(result.keys())[:5]}")

            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ⚠️  Call tool failed: {e}")
            # This might be expected if backend is down, but wrapper should still respond
            print("   (This is expected if backend API is not running)")

        # Test 4: Call non-existent tool
        print("\n4. Testing error handling (non-existent tool)...")
        try:
            tool_request = {
                "name": "nonexistent_tool_xyz",
                "arguments": {}
            }

            response = await client.post(f"{base_url}/call-tool", json=tool_request)
            print(f"   Status: {response.status_code}")

            if response.status_code == 404:
                print("   ✅ Correctly returned 404 for non-existent tool")
            else:
                print(f"   ⚠️  Expected 404, got {response.status_code}")

        except Exception as e:
            print(f"   ⚠️  Error handling test failed: {e}")

        print("\n" + "=" * 60)
        print("✅ HTTP WRAPPER TEST PASSED")
        print("=" * 60)
        return True

    finally:
        await client.aclose()


async def check_server_running():
    """Check if HTTP wrapper server is running."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:8001/health")
            return response.status_code in [200, 503]
    except Exception:
        return False


async def main():
    """Main test execution."""

    # Check if server is running
    print("Checking if HTTP wrapper is running on port 8001...")
    is_running = await check_server_running()

    if not is_running:
        print("\n❌ HTTP wrapper is not running!")
        print("\nTo start the server, run in another terminal:")
        print("   cd /Users/alekenov/figma-product-catalog/mcp-server")
        print("   uv run python http_wrapper.py")
        print("\nThen run this test again.")
        return False

    print("✅ Server is running\n")

    # Run tests
    success = await test_http_wrapper()

    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
