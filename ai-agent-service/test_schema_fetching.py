"""
Test dynamic schema fetching from MCP server.

Verifies that the AI agent can fetch and cache schemas from the ToolRegistry.
"""
import asyncio
import os
import time

from agent import FlowerShopAgent


async def test_schema_fetching():
    """Test that AI agent fetches schemas from MCP server."""
    print("🧪 Testing AI Agent Schema Fetching Integration\n")

    # Initialize agent (requires CLAUDE_API_KEY)
    api_key = os.getenv("CLAUDE_API_KEY", "test-key-not-used-for-schema-fetch")
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

    agent = FlowerShopAgent(
        api_key=api_key,
        mcp_server_url=mcp_url,
        shop_id=8
    )

    # Test 1: Fetch schemas for the first time
    print("📥 Test 1: Initial schema fetch...")
    start = time.time()
    schemas = await agent._get_tools_schema()
    duration = time.time() - start

    assert len(schemas) > 0, "Should fetch at least one schema"
    assert all("name" in s for s in schemas), "All schemas should have 'name'"
    assert all("input_schema" in s for s in schemas), "All schemas should have 'input_schema'"

    print(f"✅ Fetched {len(schemas)} schemas in {duration:.3f}s")
    print(f"   Sample tools: {[s['name'] for s in schemas[:5]]}")

    # Test 2: Verify caching (should be instant)
    print("\n💾 Test 2: Cached schema fetch...")
    start = time.time()
    cached_schemas = await agent._get_tools_schema()
    duration = time.time() - start

    assert len(cached_schemas) == len(schemas), "Cached schemas should match original"
    assert duration < 0.01, f"Cached fetch should be instant, took {duration:.3f}s"

    print(f"✅ Retrieved {len(cached_schemas)} schemas from cache in {duration:.6f}s")

    # Test 3: Verify schema structure matches Claude expectations
    print("\n🔍 Test 3: Schema structure validation...")

    sample_schema = schemas[0]
    required_fields = ["name", "description", "input_schema"]
    for field in required_fields:
        assert field in sample_schema, f"Schema missing required field: {field}"

    input_schema = sample_schema["input_schema"]
    assert input_schema["type"] == "object", "input_schema should be an object"
    assert "properties" in input_schema, "input_schema should have properties"

    print(f"✅ Schema structure valid")
    print(f"   Sample schema: {sample_schema['name']}")
    print(f"   Description: {sample_schema['description'][:80]}...")
    print(f"   Properties: {list(input_schema.get('properties', {}).keys())[:3]}")

    # Test 4: Verify cache expiration tracking
    print("\n⏱️  Test 4: Cache metadata...")

    assert agent._tool_schemas is not None, "Schemas should be cached"
    assert agent._schemas_fetched_at is not None, "Cache timestamp should be set"

    cache_age = time.time() - agent._schemas_fetched_at
    print(f"✅ Cache age: {cache_age:.2f}s (TTL: {agent._schema_cache_ttl}s)")

    print("\n🎉 All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_schema_fetching())
    exit(0 if success else 1)
