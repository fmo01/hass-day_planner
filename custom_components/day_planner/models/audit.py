from dataclasses import dataclass
from datetime import datetime


@dataclass
class Audit:

    version: int

    created_by: str
    created_at: datetime

    modified_by: str
    modified_at: datetime

    source: str
