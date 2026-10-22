from dataclasses import dataclass
from datetime import date

from .metadata import Audit


@dataclass(frozen=True, slots=True)
class CalendarException:
    """A calendar override."""

    id: str
    date: date
    day_type_id: str
    description: str | None = None
    audit: Audit | None = None

    def to_dict(self) -> dict:
        """Serialize object."""

        data = {
            "id": self.id,
            "date": self.date.isoformat(),
            "day_type_id": self.day_type_id,
            "description": self.description,
        }

        if self.audit is not None:
            data["audit"] = self.audit.to_dict()

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "CalendarException":
        """Deserialize object."""

        audit_data = data.get("audit")

        return cls(
            id=str(data["id"]),
            date=date.fromisoformat(
                str(data["date"]),
            ),
            day_type_id=str(data["day_type_id"]),
            description=data.get("description"),
            audit=(Audit.from_dict(audit_data) if audit_data is not None else None),
        )
