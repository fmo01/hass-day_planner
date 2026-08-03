from dataclasses import dataclass, field


@dataclass(slots=True)
class DayType:
    """A type of day."""

    id: str
    name: str

    moments: list[str] = field(
        default_factory=list
    )
