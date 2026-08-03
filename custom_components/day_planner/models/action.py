from dataclasses import dataclass


@dataclass(slots=True)
class Action:
    """An action executed during a moment."""

    service: str
    data: dict[str, str]
