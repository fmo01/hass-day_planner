"""Scheduled Day Planner event."""

from dataclasses import dataclass
from datetime import datetime

from .moment import Moment


@dataclass(frozen=True, slots=True)
class ScheduledEvent:
    """A concrete occurrence of a moment."""

    scheduled_at: datetime
    moment: Moment
