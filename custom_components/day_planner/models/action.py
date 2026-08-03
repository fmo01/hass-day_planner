from dataclasses import dataclass
from typing import Any


@dataclass
class Action:
    """Action executed by a moment."""

    service: str
    data: dict[str, Any]
