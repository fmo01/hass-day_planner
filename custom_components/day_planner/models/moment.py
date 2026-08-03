from dataclasses import dataclass, field

from .action import Action
from .audit import Audit


@dataclass(slots=True)
class Moment:
    """A logical moment of the day."""

    id: str
    name: str

    icon: str | None = None

    actions: list[Action] = field(
        default_factory=list
    )

    audit: Audit | None = None
