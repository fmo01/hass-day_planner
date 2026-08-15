from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cycle:
    """Cycle of weekly schedules."""

    id: str
    name: str
    week_schedule_ids: tuple[str, ...]

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "id": self.id,
            "name": self.name,
            "week_schedule_ids": list(self.week_schedule_ids),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Cycle":
        """Deserialize object."""

        return cls(
            id=data["id"],
            name=data["name"],
            week_schedule_ids=tuple(
                data.get(
                    "week_schedule_ids",
                    [],
                )
            ),
        )
