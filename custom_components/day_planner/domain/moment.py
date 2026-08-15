from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Moment:
    """A reusable moment of the day."""

    id: str
    name: str
    icon: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Serialize object."""

        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
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
        )
