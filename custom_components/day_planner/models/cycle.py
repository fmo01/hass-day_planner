from dataclasses import dataclass, field

from .week_pattern import WeekPattern


@dataclass
class Cycle:
    """A cycle of one or more weeks."""

    id: str
    name: str

    weeks: list[WeekPattern] = field(
        default_factory=list
    )
