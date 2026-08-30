from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Action:
    """An action executed during a moment."""

    id: str
    service: str
    data: dict[str, Any]

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "id": self.id,
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
            id=str(data["id"]),
            service=str(data["service"]),
            data=dict(data.get("data", {})),
        )
