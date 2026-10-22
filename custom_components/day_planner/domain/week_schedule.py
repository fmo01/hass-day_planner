from dataclasses import dataclass

from .metadata import Audit


@dataclass(frozen=True, slots=True)
class WeekSchedule:
    """Weekly schedule."""

    id: str
    name: str

    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str
    audit: Audit | None = None

    def to_dict(self) -> dict:
        """Serialize object."""

        data = {
            "id": self.id,
            "name": self.name,
            "monday": self.monday,
            "tuesday": self.tuesday,
            "wednesday": self.wednesday,
            "thursday": self.thursday,
            "friday": self.friday,
            "saturday": self.saturday,
            "sunday": self.sunday,
        }

        if self.audit is not None:
            data["audit"] = self.audit.to_dict()

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "WeekSchedule":
        """Deserialize object."""

        audit_data = data.get("audit")

        return cls(
            id=data["id"],
            name=data["name"],
            monday=data["monday"],
            tuesday=data["tuesday"],
            wednesday=data["wednesday"],
            thursday=data["thursday"],
            friday=data["friday"],
            saturday=data["saturday"],
            sunday=data["sunday"],
            audit=(Audit.from_dict(audit_data) if audit_data is not None else None),
        )
