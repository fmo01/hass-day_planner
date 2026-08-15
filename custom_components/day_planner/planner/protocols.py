"""Planner protocols."""

from typing import Protocol


class HasId(Protocol):
    """Protocol for objects exposing an identifier."""

    id: str
