from dataclasses import dataclass

from .action import Action
from .metadata import Audit


@dataclass(frozen=True, slots=True)
class Moment:
    """A reusable moment of the day."""

    id: str
    name: str
    icon: str | None = None
    actions: tuple[Action, ...] = ()
    audit: Audit | None = None

    def to_dict(self) -> dict:
        """Serialize object."""

        data = {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "actions": [action.to_dict() for action in self.actions],
        }

        if self.audit is not None:
            data["audit"] = self.audit.to_dict()

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Moment":
        """Deserialize object."""

        audit_data = data.get("audit")

        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            icon=data.get("icon"),
            actions=tuple(
                Action.from_dict(action)
                for action in data.get(
                    "actions",
                    [],
                )
            ),
            audit=(Audit.from_dict(audit_data) if audit_data is not None else None),
        )
