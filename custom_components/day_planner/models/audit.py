from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Audit:
    """Track object modifications."""

    created_by: str
    created_at: datetime

    modified_by: str
    modified_at: datetime
