"""Scheduling logic for Day Planner."""

from datetime import date, datetime, timedelta, timezone

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

    @staticmethod
    def _comparison_time(
        value: datetime,
    ) -> datetime:
        """Compare timezone-aware datetimes using UTC."""

        if value.tzinfo is not None:
            return value.astimezone(timezone.utc)

        return value

    @staticmethod
    def _normalize_scheduled_at(
        scheduled_at: datetime,
        reference: datetime,
    ) -> datetime:
        """Apply the local timezone and handle missing clock times."""

        if scheduled_at.tzinfo is not None or reference.tzinfo is None:
            return scheduled_at

        local = scheduled_at.replace(
            tzinfo=reference.tzinfo,
            fold=0,
        )

        while True:
            roundtrip = local.astimezone(timezone.utc).astimezone(reference.tzinfo)

            if roundtrip.replace(tzinfo=None) == local.replace(tzinfo=None):
                return local

            local = (local + timedelta(minutes=1)).replace(
                second=0,
                microsecond=0,
                fold=0,
            )

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

    def events_at(
        self,
        scheduled_at: datetime,
    ) -> tuple[ScheduledEvent, ...]:
        """Return all events executed at the given instant."""

        events = []
        target = self._comparison_time(scheduled_at)

        for event in self.events_for_date(scheduled_at.date()):
            event_time = self._normalize_scheduled_at(
                event.scheduled_at,
                scheduled_at,
            )

            if self._comparison_time(event_time) == target:
                events.append(
                    ScheduledEvent(
                        scheduled_at=event_time,
                        moment=event.moment,
                    )
                )

        return tuple(events)

    def next_event(
        self,
        now: datetime,
        max_days: int = 366,
    ) -> ScheduledEvent | None:
        """Return the next scheduled event."""

        for day_offset in range(max_days + 1):
            target_date = now.date() + timedelta(days=day_offset)

            for event in self.events_for_date(target_date):
                scheduled_at = self._normalize_scheduled_at(
                    event.scheduled_at,
                    now,
                )

                if self._comparison_time(scheduled_at) > self._comparison_time(now):
                    if scheduled_at == event.scheduled_at:
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
                scheduled_at = self._normalize_scheduled_at(
                    event.scheduled_at,
                    now,
                )

            event_start = self._comparison_time(scheduled_at)
            event_end = event_start + timedelta(minutes=1)

            if event_start <= self._comparison_time(now) < event_end:
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

        for event in self.events_for_date(now.date()):
            scheduled_at = self._normalize_scheduled_at(
                event.scheduled_at,
                now,
            )

            if self._comparison_time(scheduled_at) > self._comparison_time(now):
                break

            if scheduled_at == event.scheduled_at:
                current = event
            else:
                current = ScheduledEvent(
                    scheduled_at=scheduled_at,
                    moment=event.moment,
                )

        return current
