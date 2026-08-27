from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Action:
    """An action executed during a moment."""

    service: str
    data: dict[str, Any]

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "service": self.service,
            "data": self.data,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Action":
        """Deserialize object."""

        return cls(
            service=str(data["service"]),
            data=dict(data.get("data", {})),
        )
