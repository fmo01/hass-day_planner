from dataclasses import dataclass


@dataclass
class WeekPattern:
    """A weekly schedule."""

    id: str
    name: str

    monday: str | None = None
    tuesday: str | None = None
    wednesday: str | None = None
    thursday: str | None = None
    friday: str | None = None
    saturday: str | None = None
    sunday: str | None = None
