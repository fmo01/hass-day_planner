from dataclasses import dataclass
from datetime import date


@dataclass
class PlannerException:
    """Calendar exception."""

    date: date
    day_type_id: str
    description: str
