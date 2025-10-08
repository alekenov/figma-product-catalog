"""
Regression test for Optional[T] type conversion bug.

Before fix: Optional[int] → {"type": "string"} (WRONG!)
After fix:  Optional[int] → {"type": "integer"} (CORRECT)

This test ensures that Optional types are correctly unwrapped and their
inner types are properly converted to JSON Schema.
"""
import pytest
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Add parent directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.registry import ToolRegistry


class TestOptionalTypeConversion:
    """Test that Optional[T] types are correctly converted to JSON Schema."""

    def test_optional_int_converts_to_integer(self):
        """Optional[int] should become {"type": "integer"}, not {"type": "string"}."""
        schema = ToolRegistry._python_type_to_json_schema(Optional[int])
        assert schema == {"type": "integer"}, f"Expected integer, got {schema}"

    def test_optional_str_converts_to_string(self):
        """Optional[str] should become {"type": "string"}."""
        schema = ToolRegistry._python_type_to_json_schema(Optional[str])
        assert schema == {"type": "string"}, f"Expected string, got {schema}"

    def test_optional_float_converts_to_number(self):
        """Optional[float] should become {"type": "number"}."""
        schema = ToolRegistry._python_type_to_json_schema(Optional[float])
        assert schema == {"type": "number"}, f"Expected number, got {schema}"

    def test_optional_bool_converts_to_boolean(self):
        """Optional[bool] should become {"type": "boolean"}."""
        schema = ToolRegistry._python_type_to_json_schema(Optional[bool])
        assert schema == {"type": "boolean"}, f"Expected boolean, got {schema}"

    def test_plain_int_converts_to_integer(self):
        """int (without Optional) should become {"type": "integer"}."""
        schema = ToolRegistry._python_type_to_json_schema(int)
        assert schema == {"type": "integer"}, f"Expected integer, got {schema}"

    def test_plain_str_converts_to_string(self):
        """str (without Optional) should become {"type": "string"}."""
        schema = ToolRegistry._python_type_to_json_schema(str)
        assert schema == {"type": "string"}, f"Expected string, got {schema}"

    def test_list_of_int_converts_correctly(self):
        """List[int] should become {"type": "array", "items": {"type": "integer"}}."""
        schema = ToolRegistry._python_type_to_json_schema(List[int])
        assert schema == {
            "type": "array",
            "items": {"type": "integer"}
        }, f"Expected array of integers, got {schema}"

    def test_optional_list_of_dict_converts_correctly(self):
        """Optional[List[Dict]] should unwrap to List[Dict] → array of objects."""
        schema = ToolRegistry._python_type_to_json_schema(Optional[List[Dict]])
        assert schema == {
            "type": "array",
            "items": {"type": "object"}
        }, f"Expected array of objects, got {schema}"

    def test_dict_converts_to_object(self):
        """Dict should become {"type": "object"}."""
        schema = ToolRegistry._python_type_to_json_schema(Dict)
        assert schema == {"type": "object"}, f"Expected object, got {schema}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
