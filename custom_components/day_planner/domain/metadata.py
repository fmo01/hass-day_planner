"""Audit metadata for Day Planner objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Audit:
    """Track object modifications."""

    created_by: str
    created_at: datetime
    modified_by: str
    modified_at: datetime

    def to_dict(self) -> dict:
        """Serialize audit metadata."""

        return {
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "modified_by": self.modified_by,
            "modified_at": self.modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Audit":
        """Deserialize audit metadata."""

        return cls(
            created_by=str(data["created_by"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_by=str(data["modified_by"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
        )
