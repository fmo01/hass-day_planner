"""Calendar platform for Day Planner."""

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, INTEGRATION_NAME, SIGNAL_PLANNER_UPDATED
from .integration_info import integration_attributes
from .runtime import DayPlannerRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Day Planner calendar."""

    runtime: DayPlannerRuntimeData = entry.runtime_data

    async_add_entities(
        [
            DayPlannerCalendar(runtime),
        ]
    )


class DayPlannerCalendar(CalendarEntity):
    """Calendar exposing Day Planner events."""

    _attr_has_entity_name = False
    _attr_name = f"{INTEGRATION_NAME} Planning"

    def __init__(
        self,
        runtime: DayPlannerRuntimeData,
    ) -> None:
        """Initialize calendar."""

        self._runtime = runtime
        self._attr_unique_id = f"{DOMAIN}_calendar"

    async def async_added_to_hass(self) -> None:
        """Register update listener."""

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_PLANNER_UPDATED,
                self._handle_planner_updated,
            )
        )

    @callback
    def _handle_planner_updated(self) -> None:
        """Handle planner configuration update."""

        self.async_write_ha_state()
        self.async_update_event_listeners()

    @property
    def event(
        self,
    ) -> CalendarEvent | None:
        """Return current or next event."""

        now = dt_util.now()

        scheduled_event = self._runtime.scheduler.current_event(now)

        if scheduled_event is None:
            scheduled_event = self._runtime.scheduler.next_event(now)

        if scheduled_event is None:
            return None

        return self._to_calendar_event(
            scheduled_event.scheduled_at,
            scheduled_event.moment.name,
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a range."""

        events: list[CalendarEvent] = []

        current_date = start_date.date()

        while current_date <= end_date.date():
            for scheduled_event in self._runtime.scheduler.events_for_date(
                current_date
            ):
                scheduled_at = scheduled_event.scheduled_at

                if scheduled_at.tzinfo is None:
                    scheduled_at = dt_util.as_local(
                        scheduled_at.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
                    )

                event_end = scheduled_at + timedelta(minutes=1)

                if event_end > start_date and scheduled_at < end_date:
                    events.append(
                        self._to_calendar_event(
                            scheduled_at,
                            scheduled_event.moment.name,
                        )
                    )

            current_date += timedelta(days=1)

        return sorted(
            events,
            key=lambda item: item.start,
        )

    @staticmethod
    def _to_calendar_event(
        scheduled_at: datetime,
        name: str,
    ) -> CalendarEvent:
        """Convert scheduled event to Home Assistant event."""

        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

        return CalendarEvent(
            start=scheduled_at,
            end=scheduled_at + timedelta(minutes=1),
            summary=name,
        )

    @property
    def extra_state_attributes(
        self,
    ) -> dict:
        """Return Day Planner integration information."""

        attributes = {
            **integration_attributes(),
        }

        return attributes
