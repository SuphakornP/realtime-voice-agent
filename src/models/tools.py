"""Function tool model."""

from typing import Any, Callable

from pydantic import BaseModel, Field, field_validator


class FunctionTool(BaseModel):
    """Represents a callable function tool."""

    name: str = Field(
        ...,
        description="Tool name (must be valid Python identifier)",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Human-readable description of what the tool does",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema for tool parameters",
    )

    @field_validator("name")
    @classmethod
    def validate_name_is_identifier(cls, v: str) -> str:
        """Validate name is a valid Python identifier."""
        if not v.isidentifier():
            raise ValueError(f"Tool name must be a valid Python identifier: {v}")
        return v

    model_config = {"arbitrary_types_allowed": True}


__all__ = ["FunctionTool"]
