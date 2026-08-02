from dataclasses import dataclass


@dataclass
class Moment:

    id: str
    name: str
    icon: str
    color: str

    actions: list

    audit: object
