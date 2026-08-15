from dataclasses import dataclass


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

    def to_dict(self) -> dict[str, str]:
        """Serialize object."""

        return {
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

    @classmethod
    def from_dict(
        cls,
        data: dict[str, str],
    ) -> "WeekSchedule":
        """Deserialize object."""

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
        )
