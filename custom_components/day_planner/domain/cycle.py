from dataclasses import dataclass
from datetime import date

from .metadata import Audit


@dataclass(frozen=True, slots=True)
class Cycle:
    """Cycle of weekly schedules."""

    id: str
    name: str
    start_date: date
    week_schedule_ids: tuple[str, ...]
    audit: Audit | None = None

    def to_dict(self) -> dict:
        """Serialize object."""

        data = {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "week_schedule_ids": list(self.week_schedule_ids),
        }

        if self.audit is not None:
            data["audit"] = self.audit.to_dict()

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Cycle":
        """Deserialize object."""

        audit_data = data.get("audit")

        return cls(
            id=data["id"],
            name=data["name"],
            start_date=date.fromisoformat(
                data["start_date"],
            ),
            week_schedule_ids=tuple(
                data.get(
                    "week_schedule_ids",
                    [],
                )
            ),
            audit=(Audit.from_dict(audit_data) if audit_data is not None else None),
        )
