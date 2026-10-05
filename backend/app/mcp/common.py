"""Shared helpers for MCP servers: UUID parsing and consistent error payloads."""
import uuid


def parse_uuid(value: str, field_name: str = "id") -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"Invalid {field_name}: '{value}' is not a valid UUID") from exc
