"""Day type model."""

from dataclasses import dataclass

from .metadata import Audit
from .scheduled_moment import ScheduledMoment


@dataclass(frozen=True, slots=True)
class DayType:
    """A type of day."""

    id: str
    name: str
    scheduled_moments: tuple[ScheduledMoment, ...]
    audit: Audit | None = None

    def to_dict(self) -> dict:
        """Serialize object."""

        data = {
            "id": self.id,
            "name": self.name,
            "scheduled_moments": [item.to_dict() for item in self.scheduled_moments],
        }

        if self.audit is not None:
            data["audit"] = self.audit.to_dict()

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "DayType":
        """Deserialize object."""

        audit_data = data.get("audit")

        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            scheduled_moments=tuple(
                ScheduledMoment.from_dict(item)
                for item in data.get(
                    "scheduled_moments",
                    [],
                )
            ),
            audit=(Audit.from_dict(audit_data) if audit_data is not None else None),
        )
