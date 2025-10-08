"""
Unit tests for ToolRegistry.
Tests tool registration and discovery mechanisms.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.registry import ToolRegistry, ToolMetadata


class TestToolRegistry:
    """Test suite for ToolRegistry."""

    def setup_method(self):
        """Clear registry before each test."""
        ToolRegistry._tools = {}
        ToolRegistry._initialized = False

    def test_register_decorator_basic(self):
        """Test that @register decorator adds tool to registry."""
        @ToolRegistry.register(domain="test", requires_auth=False)
        async def test_tool():
            """Test tool docstring."""
            return "test result"

        assert "test_tool" in ToolRegistry._tools
        metadata = ToolRegistry._tools["test_tool"]
        assert metadata.name == "test_tool"
        assert metadata.domain == "test"
        assert metadata.requires_auth is False

    def test_register_decorator_with_auth(self):
        """Test registering tool that requires authentication."""
        @ToolRegistry.register(domain="admin", requires_auth=True)
        async def admin_tool():
            return "admin result"

        metadata = ToolRegistry._tools["admin_tool"]
        assert metadata.requires_auth is True

    def test_register_decorator_public_tool(self):
        """Test registering public tool."""
        @ToolRegistry.register(domain="public", requires_auth=False, is_public=True)
        async def public_tool():
            return "public result"

        metadata = ToolRegistry._tools["public_tool"]
        assert metadata.is_public is True

    def test_get_tool_exists(self):
        """Test getting existing tool function."""
        @ToolRegistry.register(domain="test")
        async def my_tool():
            return "result"

        func = ToolRegistry.get_tool("my_tool")
        assert func is not None
        assert callable(func)

    def test_get_tool_not_exists(self):
        """Test getting non-existent tool returns None."""
        func = ToolRegistry.get_tool("nonexistent_tool")
        assert func is None

    def test_get_metadata(self):
        """Test getting tool metadata."""
        @ToolRegistry.register(domain="test", requires_auth=False)
        async def metadata_test():
            """Tool with metadata."""
            return "result"

        metadata = ToolRegistry.get_metadata("metadata_test")
        assert metadata is not None
        assert isinstance(metadata, ToolMetadata)
        assert metadata.name == "metadata_test"
        assert metadata.domain == "test"
        assert "Tool with metadata" in metadata.description

    def test_list_tools(self):
        """Test listing all registered tool names."""
        @ToolRegistry.register(domain="test1")
        async def tool1():
            pass

        @ToolRegistry.register(domain="test2")
        async def tool2():
            pass

        tools = ToolRegistry.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools
        assert len(tools) >= 2

    def test_list_by_domain(self):
        """Test filtering tools by domain."""
        @ToolRegistry.register(domain="auth")
        async def login():
            pass

        @ToolRegistry.register(domain="products")
        async def list_products():
            pass

        @ToolRegistry.register(domain="auth")
        async def logout():
            pass

        auth_tools = ToolRegistry.list_by_domain("auth")
        assert len(auth_tools) == 2
        assert all(t.domain == "auth" for t in auth_tools)

    def test_list_public_tools(self):
        """Test listing only public tools."""
        @ToolRegistry.register(domain="test", is_public=True)
        async def public_tool():
            pass

        @ToolRegistry.register(domain="test", is_public=False)
        async def private_tool():
            pass

        public_tools = ToolRegistry.list_public_tools()
        assert "public_tool" in public_tools
        assert "private_tool" not in public_tools

    def test_get_tool_map(self):
        """Test getting dictionary of all tools."""
        @ToolRegistry.register(domain="test")
        async def tool_a():
            pass

        @ToolRegistry.register(domain="test")
        async def tool_b():
            pass

        tool_map = ToolRegistry.get_tool_map()
        assert isinstance(tool_map, dict)
        assert "tool_a" in tool_map
        assert "tool_b" in tool_map
        assert callable(tool_map["tool_a"])

    def test_validate_success(self):
        """Test validation succeeds with registered tools."""
        @ToolRegistry.register(domain="test")
        async def test_tool():
            pass

        # Should not raise
        ToolRegistry.validate()
        assert ToolRegistry._initialized is True

    def test_validate_empty_registry(self):
        """Test validation fails with empty registry."""
        # Registry is empty from setup_method
        with pytest.raises(ValueError, match="No tools registered"):
            ToolRegistry.validate()

    def test_tool_function_executes(self):
        """Test that registered tool function can be executed."""
        @ToolRegistry.register(domain="test")
        async def executable_tool(x: int):
            return x * 2

        func = ToolRegistry.get_tool("executable_tool")
        import asyncio
        result = asyncio.run(func(5))
        assert result == 10

    def test_docstring_preserved(self):
        """Test that tool docstring is preserved."""
        @ToolRegistry.register(domain="test")
        async def documented_tool():
            """This is a test tool with documentation."""
            pass

        metadata = ToolRegistry.get_metadata("documented_tool")
        assert "test tool with documentation" in metadata.description


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
