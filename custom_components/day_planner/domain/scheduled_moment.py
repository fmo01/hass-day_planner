from dataclasses import dataclass

from .time_definition import TimeDefinition


@dataclass(frozen=True, slots=True)
class ScheduledMoment:
    """A moment scheduled in a day type."""

    moment_id: str
    time_definition: TimeDefinition

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "moment_id": self.moment_id,
            "time_definition": (self.time_definition.to_dict()),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ScheduledMoment":
        """Deserialize object."""

        return cls(
            moment_id=str(data["moment_id"]),
            time_definition=(TimeDefinition.from_dict(data["time_definition"])),
        )
