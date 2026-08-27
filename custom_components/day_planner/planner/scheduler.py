"""Scheduling logic for Day Planner."""

from datetime import date, datetime, timedelta

from ..domain.scheduled_event import ScheduledEvent
from .resolver import PlannerResolver


class PlannerScheduler:
    """Calculate Day Planner scheduled events."""

    def __init__(
        self,
        resolver: PlannerResolver,
    ) -> None:
        """Initialize scheduler."""

        self._resolver = resolver

    def events_for_date(
        self,
        target_date: date,
    ) -> tuple[ScheduledEvent, ...]:
        """Return all scheduled events for a date."""

        events = []

        for scheduled, moment in self._resolver.resolve_schedule(target_date):
            scheduled_at = datetime.combine(
                target_date,
                scheduled.time_definition.fixed_time,
            )

            events.append(
                ScheduledEvent(
                    scheduled_at=scheduled_at,
                    moment=moment,
                )
            )

        return tuple(
            sorted(
                events,
                key=lambda event: event.scheduled_at,
            )
        )

    def next_event(
        self,
        now: datetime,
        max_days: int = 366,
    ) -> ScheduledEvent | None:
        """Return the next scheduled event."""

        for day_offset in range(max_days + 1):
            target_date = now.date() + timedelta(days=day_offset)

            for event in self.events_for_date(target_date):
                if event.scheduled_at > now:
                    return event

        return None
