from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class CalendarException:
    """A calendar override."""

    id: str
    date: date
    day_type_id: str
    description: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Serialize object."""

        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "day_type_id": self.day_type_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, str | None],
    ) -> "CalendarException":
        """Deserialize object."""

        return cls(
            id=str(data["id"]),
            date=date.fromisoformat(str(data["date"])),
            day_type_id=str(data["day_type_id"]),
            description=data.get("description"),
        )
