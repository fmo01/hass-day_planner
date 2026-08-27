from dataclasses import dataclass

from .action import Action


@dataclass(frozen=True, slots=True)
class Moment:
    """A reusable moment of the day."""

    id: str
    name: str
    icon: str | None = None
    actions: tuple[Action, ...] = ()

    def to_dict(self) -> dict[str, str | None]:
        """Serialize object."""

        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "actions": [action.to_dict() for action in self.actions],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, str | None],
    ) -> "Moment":
        """Deserialize object."""

        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            icon=data.get("icon"),
            actions=tuple(
                Action.from_dict(action) for action in data.get("actions", [])
            ),
        )
