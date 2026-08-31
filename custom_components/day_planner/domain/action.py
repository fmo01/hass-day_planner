"""Day Planner action model."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Action:
    """An action executed during a moment."""

    id: str
    sequence: list[dict[str, Any]]

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "id": self.id,
            "sequence": self.sequence,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Action":
        """Deserialize object."""

        return cls(
            id=str(data["id"]),
            sequence=list(
                data.get(
                    "sequence",
                    [],
                )
            ),
        )
