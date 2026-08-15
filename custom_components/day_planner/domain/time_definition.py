from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True, slots=True)
class TimeDefinition:
    """Definition of a scheduled time."""

    fixed_time: time

    def to_dict(self) -> dict[str, str]:
        """Serialize object."""

        return {
            "fixed_time": self.fixed_time.isoformat(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, str],
    ) -> "TimeDefinition":
        """Deserialize object."""

        return cls(
            fixed_time=time.fromisoformat(
                data["fixed_time"]
            )
        )
