"""Day Planner action model."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Action:
    """An action executed during a moment."""

    id: str
    sequence: list[dict[str, Any]]
    label: str | None = None

    def __post_init__(self) -> None:
        """Initialize derived values."""

        if self.label is None:
            object.__setattr__(
                self,
                "label",
                self.id,
            )

    def to_dict(self) -> dict:
        """Serialize object."""

        return {
            "id": self.id,
            "label": self.label,
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
            label=str(
                data.get(
                    "label",
                    data["id"],
                )
            ),
            sequence=list(
                data.get(
                    "sequence",
                    [],
                )
            ),
        )
