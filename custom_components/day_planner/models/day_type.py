from dataclasses import dataclass, field

from .moment import Moment


@dataclass
class DayType:
    """A type of day."""

    id: str
    name: str

    moments: list[Moment] = field(default_factory=list)
