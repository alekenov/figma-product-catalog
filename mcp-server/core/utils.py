"""
Utility helpers shared across MCP domains.

These helpers reduce the amount of boilerplate around assembling request
payloads and query parameters. They intentionally avoid any clever defaults so
that call sites stay explicit about required values.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


def merge_required_optional(
    required: Mapping[str, Any],
    optional: Optional[Mapping[str, Optional[Any]]] = None,
) -> Dict[str, Any]:
    """
    Build a dictionary that keeps all required keys and skips optional `None`.

    Args:
        required: Key/value pairs that must always be present.
        optional: Key/value pairs that should only be included when the value
            is not None.

    Returns:
        New dictionary containing ``required`` plus all non-None optional items.
    """
    result: Dict[str, Any] = dict(required)
    if not optional:
        return result

    for key, value in optional.items():
        if value is not None:
            result[key] = value
    return result


def drop_none(data: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of the mapping without keys whose value is ``None``.

    This is handy when constructing JSON payloads: omitting the key entirely
    tends to be more ergonomic than sending explicit ``null`` values.
    """
    return {key: value for key, value in data.items() if value is not None}
