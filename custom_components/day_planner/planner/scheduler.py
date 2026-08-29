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
                scheduled_at = event.scheduled_at

                if scheduled_at.tzinfo is None and now.tzinfo is not None:
                    scheduled_at = scheduled_at.replace(tzinfo=now.tzinfo)

                if scheduled_at > now:
                    if scheduled_at is event.scheduled_at:
                        return event

                    return ScheduledEvent(
                        scheduled_at=scheduled_at,
                        moment=event.moment,
                    )

        return None

    def current_event(
        self,
        now: datetime,
    ) -> ScheduledEvent | None:
        """Return the currently active event."""

        for event in self.events_for_date(now.date()):
            scheduled_at = event.scheduled_at

            if scheduled_at.tzinfo is None and now.tzinfo is not None:
                scheduled_at = scheduled_at.replace(tzinfo=now.tzinfo)

            event_end = scheduled_at + timedelta(minutes=1)

            if scheduled_at <= now < event_end:
                if scheduled_at is event.scheduled_at:
                    return event

                return ScheduledEvent(
                    scheduled_at=scheduled_at,
                    moment=event.moment,
                )

        return None

    def current_moment(
        self,
        now: datetime,
    ) -> ScheduledEvent | None:
        """Return the latest event reached for the current day."""

        current: ScheduledEvent | None = None

        for event in self.events_for_date(
            now.date()
        ):
            scheduled_at = event.scheduled_at

            if (
                scheduled_at.tzinfo is None
                and now.tzinfo is not None
            ):
                scheduled_at = scheduled_at.replace(
                    tzinfo=now.tzinfo
                )

            if scheduled_at > now:
                break

            if scheduled_at is event.scheduled_at:
                current = event
            else:
                current = ScheduledEvent(
                    scheduled_at=scheduled_at,
                    moment=event.moment,
                )

        return current

