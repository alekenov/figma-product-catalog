"""
Metadata-driven tool registry.
Eliminates hardcoded tool dictionaries by auto-registering tools via decorators.
"""
from typing import Callable, Dict, List, Optional, Any, Union, get_origin, get_args
from dataclasses import dataclass
import logging
import inspect

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata about a registered tool."""

    name: str
    func: Callable
    domain: str  # "auth", "products", "orders", etc.
    requires_auth: bool
    description: str
    is_public: bool  # Whether tool is available without authentication


class ToolRegistry:
    """
    Central registry for all MCP tools.

    Usage:
        @ToolRegistry.register(domain="auth", requires_auth=False)
        @mcp.tool()
        async def login(phone: str, password: str):
            ...

    Benefits:
    - Single source of truth for tool metadata
    - Auto-generates tool mappings for HTTP wrapper
    - Easy to query tools by domain or auth requirements
    """

    _tools: Dict[str, ToolMetadata] = {}
    _initialized: bool = False

    @classmethod
    def register(
        cls,
        domain: str,
        requires_auth: bool = True,
        is_public: bool = False
    ):
        """
        Decorator to register a tool with metadata.

        Args:
            domain: Tool domain (auth, products, orders, etc.)
            requires_auth: Whether tool requires JWT token
            is_public: Whether tool is available without auth

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            tool_name = func.__name__
            metadata = ToolMetadata(
                name=tool_name,
                func=func,
                domain=domain,
                requires_auth=requires_auth,
                description=func.__doc__ or "",
                is_public=is_public
            )

            cls._tools[tool_name] = metadata
            logger.debug(f"Registered tool: {tool_name} (domain={domain})")

            return func

        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Optional[Callable]:
        """
        Get tool function by name.

        Args:
            name: Tool name

        Returns:
            Tool function or None if not found
        """
        metadata = cls._tools.get(name)
        return metadata.func if metadata else None

    @classmethod
    def get_metadata(cls, name: str) -> Optional[ToolMetadata]:
        """
        Get tool metadata by name.

        Args:
            name: Tool name

        Returns:
            ToolMetadata or None if not found
        """
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tool names."""
        return list(cls._tools.keys())

    @classmethod
    def list_by_domain(cls, domain: str) -> List[ToolMetadata]:
        """
        List all tools in a specific domain.

        Args:
            domain: Domain name (e.g., "auth", "products")

        Returns:
            List of tool metadata
        """
        return [
            metadata
            for metadata in cls._tools.values()
            if metadata.domain == domain
        ]

    @classmethod
    def list_public_tools(cls) -> List[str]:
        """List all public tools (no auth required)."""
        return [
            name
            for name, metadata in cls._tools.items()
            if metadata.is_public
        ]

    @classmethod
    def get_tool_map(cls) -> Dict[str, Callable]:
        """
        Get dictionary mapping tool names to functions.
        Used by HTTP wrapper for /call-tool endpoint.

        Returns:
            Dictionary of {tool_name: tool_function}
        """
        return {name: metadata.func for name, metadata in cls._tools.items()}

    @classmethod
    def print_summary(cls) -> None:
        """Print summary of registered tools by domain."""
        domains = {}
        for metadata in cls._tools.values():
            if metadata.domain not in domains:
                domains[metadata.domain] = []
            domains[metadata.domain].append(metadata.name)

        logger.info("📋 Tool Registry Summary:")
        for domain, tools in sorted(domains.items()):
            logger.info(f"  {domain}: {len(tools)} tools")
            for tool_name in sorted(tools):
                logger.info(f"    - {tool_name}")

        logger.info(f"\nTotal: {len(cls._tools)} tools across {len(domains)} domains")

    @classmethod
    def _python_type_to_json_schema(cls, python_type: Any) -> Dict[str, Any]:
        """
        Convert Python type annotation to JSON Schema type.

        Args:
            python_type: Python type annotation

        Returns:
            JSON Schema type dict
        """
        origin = get_origin(python_type)

        # Handle Union types (including Optional[T] which is Union[T, None])
        if origin is Union:
            args = get_args(python_type)
            # Filter out NoneType to get the actual type(s)
            non_none_types = [arg for arg in args if arg is not type(None)]

            # If only one non-None type remains, it's Optional[T] → treat as T
            if len(non_none_types) == 1:
                return cls._python_type_to_json_schema(non_none_types[0])

            # If multiple non-None types (rare), recurse on first one
            # This handles edge cases like Union[int, str] by picking int
            if len(non_none_types) > 1:
                return cls._python_type_to_json_schema(non_none_types[0])

            # If all types were None (shouldn't happen), default to string
            return {"type": "string"}

        # Handle List[T]
        if origin is list or origin is List:
            args = get_args(python_type)
            item_type = args[0] if args else Any
            return {
                "type": "array",
                "items": cls._python_type_to_json_schema(item_type)
            }

        # Handle Dict[K, V]
        if origin is dict or origin is Dict:
            return {"type": "object"}

        # Basic types
        type_mapping = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
        }

        return type_mapping.get(python_type, {"type": "string"})

    @classmethod
    def _extract_parameter_schema(cls, param: inspect.Parameter) -> Dict[str, Any]:
        """
        Extract JSON Schema for a function parameter.

        Args:
            param: Function parameter from inspect.signature()

        Returns:
            JSON Schema dict for the parameter
        """
        schema = cls._python_type_to_json_schema(param.annotation)

        # Add default if present
        if param.default != inspect.Parameter.empty:
            schema["default"] = param.default

        return schema

    @classmethod
    def generate_claude_schema(cls, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Generate Claude-compatible schema for a tool.

        Args:
            tool_name: Name of the registered tool

        Returns:
            Claude tool schema or None if tool not found
        """
        metadata = cls.get_metadata(tool_name)
        if not metadata:
            return None

        # Extract function signature
        sig = inspect.signature(metadata.func)

        # Build properties and required list
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip self, request_id, and other internal parameters
            if param_name in ('self', 'request_id'):
                continue

            param_schema = cls._extract_parameter_schema(param)
            properties[param_name] = param_schema

            # Mark as required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        # Build Claude schema format
        schema = {
            "name": tool_name,
            "description": metadata.description.strip() or f"{tool_name} tool",
            "input_schema": {
                "type": "object",
                "properties": properties,
            }
        }

        # Add required fields if any
        if required:
            schema["input_schema"]["required"] = required

        return schema

    @classmethod
    def generate_all_schemas(cls) -> List[Dict[str, Any]]:
        """
        Generate Claude-compatible schemas for all registered tools.

        Returns:
            List of Claude tool schemas
        """
        schemas = []
        for tool_name in sorted(cls.list_tools()):
            schema = cls.generate_claude_schema(tool_name)
            if schema:
                schemas.append(schema)

        return schemas

    @classmethod
    def validate(cls) -> None:
        """Validate registry integrity."""
        if not cls._tools:
            raise ValueError("No tools registered in ToolRegistry")

        # Check for duplicate names (should not happen)
        if len(cls._tools) != len(set(cls._tools.keys())):
            raise ValueError("Duplicate tool names detected")

        cls._initialized = True
        logger.info(f"✅ ToolRegistry validated: {len(cls._tools)} tools registered")
