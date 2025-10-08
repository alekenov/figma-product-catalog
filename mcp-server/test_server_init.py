#!/usr/bin/env python3
"""
Test script to verify server initialization and tool registration.
Validates that all domain modules load correctly and tools are registered.
"""
import sys
from pathlib import Path

# Add current directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.registry import ToolRegistry


def test_server_initialization():
    """Test that server initializes with all expected tools."""

    print("=" * 60)
    print("MCP SERVER INITIALIZATION TEST")
    print("=" * 60)

    # Import server to trigger tool registration
    print("\n1. Importing server module...")
    try:
        import server
        print("   ✅ Server module imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import server: {e}")
        return False

    # Check tool registry
    print("\n2. Checking ToolRegistry...")
    tools = ToolRegistry.list_tools()
    tool_count = len(tools)
    print(f"   ✅ Found {tool_count} registered tools")

    if tool_count == 0:
        print("   ❌ No tools registered!")
        return False

    # Validate registry
    print("\n3. Validating registry integrity...")
    try:
        ToolRegistry.validate()
        print("   ✅ Registry validation passed")
    except Exception as e:
        print(f"   ❌ Registry validation failed: {e}")
        return False

    # List tools by domain
    print("\n4. Tools by domain:")
    domains = {}
    for tool_name in tools:
        metadata = ToolRegistry.get_metadata(tool_name)
        if metadata:
            domain = metadata.domain
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(tool_name)

    for domain, domain_tools in sorted(domains.items()):
        print(f"\n   {domain}/ ({len(domain_tools)} tools)")
        for tool_name in sorted(domain_tools):
            metadata = ToolRegistry.get_metadata(tool_name)
            auth_marker = "🔒" if metadata.requires_auth else "🔓"
            public_marker = "🌐" if metadata.is_public else "🔐"
            print(f"      {auth_marker} {public_marker} {tool_name}")

    # Check expected minimum tool count
    print("\n5. Checking minimum tool count...")
    EXPECTED_MIN_TOOLS = 40
    if tool_count >= EXPECTED_MIN_TOOLS:
        print(f"   ✅ Tool count meets expectation ({tool_count} >= {EXPECTED_MIN_TOOLS})")
    else:
        print(f"   ⚠️  Tool count below expectation ({tool_count} < {EXPECTED_MIN_TOOLS})")

    # Check that FastMCP server instance exists
    print("\n6. Checking FastMCP server instance...")
    if hasattr(server, 'mcp'):
        print(f"   ✅ FastMCP server instance found: {type(server.mcp)}")

        # Check registered tools in FastMCP
        if hasattr(server.mcp, '_tools'):
            mcp_tool_count = len(server.mcp._tools)
            print(f"   ✅ FastMCP has {mcp_tool_count} tools registered")
        else:
            print("   ⚠️  Cannot access FastMCP._tools attribute")
    else:
        print("   ❌ FastMCP server instance not found")
        return False

    print("\n" + "=" * 60)
    print("✅ SERVER INITIALIZATION TEST PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_server_initialization()
    sys.exit(0 if success else 1)
