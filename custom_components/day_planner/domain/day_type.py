from dataclasses import dataclass


from .scheduled_moment import ScheduledMoment


@dataclass(frozen=True, slots=True)
class DayType:
    """A type of day."""

    id: str
    name: str
    scheduled_moments: tuple[ScheduledMoment, ...]

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "id": self.id,
            "name": self.name,
            "scheduled_moments": [
                item.to_dict()
                for item in self.scheduled_moments
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "DayType":
        """Deserialize object."""

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
        )
