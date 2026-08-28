"""Sensor platform for Day Planner."""

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_PLANNER_UPDATED
from .runtime import DayPlannerRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Day Planner sensors."""

    runtime: DayPlannerRuntimeData = entry.runtime_data

    async_add_entities(
        [
            DayPlannerNextEventSensor(
                runtime
            ),
        ]
    )


class DayPlannerNextEventSensor(SensorEntity):
    """Sensor exposing the next Day Planner event."""

    _attr_has_entity_name = True
    _attr_name = "Next event"

    def __init__(
        self,
        runtime: DayPlannerRuntimeData,
    ) -> None:
        """Initialize sensor."""

        self._runtime = runtime
        self._attr_unique_id = (
            f"{DOMAIN}_next_event"
        )

    @property
    def native_value(
        self,
    ) -> str | None:
        """Return the next moment name."""

        event = self._next_event()

        if event is None:
            return None

        return event.moment.name

    @property
    def extra_state_attributes(
        self,
    ) -> dict:
        """Return additional event information."""

        event = self._next_event()

        if event is None:
            return {}

        return {
            "moment_id": event.moment.id,
            "scheduled_at": event.scheduled_at.isoformat(),
        }

    def _next_event(self):
        """Return the next scheduled event."""

        now: datetime = dt_util.now()

        return self._runtime.scheduler.next_event(
            now
        )

    async def async_added_to_hass(self) -> None:
        """Register update listener."""

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_PLANNER_UPDATED,
                self._handle_planner_updated,
            )
        )

    def _handle_planner_updated(self) -> None:
        """Handle planner configuration update."""

        self.async_write_ha_state()

