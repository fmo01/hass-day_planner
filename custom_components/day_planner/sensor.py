"""Sensor platform for Day Planner."""

import json
from datetime import datetime
from pathlib import Path

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, 
    INTEGRATION_NAME, 
    SIGNAL_PLANNER_UPDATED,
)
from .runtime import DayPlannerRuntimeData
from .integration_info import integration_attributes

_MANIFEST_PATH = Path(__file__).with_name("manifest.json")

with _MANIFEST_PATH.open(
    encoding="utf-8",
) as manifest_file:
    _MANIFEST = json.load(manifest_file)

INTEGRATION_VERSION = _MANIFEST["version"]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Day Planner sensors."""

    runtime: DayPlannerRuntimeData = entry.runtime_data

    async_add_entities(
        [
            DayPlannerNextEventSensor(runtime),
            DayPlannerCurrentDayTypeSensor(runtime),
            DayPlannerCurrentMomentSensor(runtime),
        ]
    )


class DayPlannerNextEventSensor(SensorEntity):
    """Sensor exposing the next Day Planner event."""

    _attr_has_entity_name = False
    _attr_name = f"{INTEGRATION_NAME} Next event"

    def __init__(
        self,
        runtime: DayPlannerRuntimeData,
    ) -> None:
        """Initialize sensor."""

        self._runtime = runtime
        self._attr_unique_id = f"{DOMAIN}_next_event"

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
            attributes = {
                **integration_attributes(),
                "moment_id": None,
                "scheduled_at": None,
            }

            return attributes

        attributes = {
            **integration_attributes(),
            "moment_id": event.moment.id,
            "scheduled_at": event.scheduled_at.isoformat(),
        }

        return attributes

    def _next_event(self):
        """Return the next scheduled event."""

        now: datetime = dt_util.now()

        return self._runtime.scheduler.next_event(now)

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


class DayPlannerCurrentDayTypeSensor(SensorEntity):
    """Sensor exposing the current Day Planner day type."""

    _attr_has_entity_name = False
    _attr_name = f"{INTEGRATION_NAME} Current day type"

    def __init__(
        self,
        runtime: DayPlannerRuntimeData,
    ) -> None:
        """Initialize sensor."""

        self._runtime = runtime
        self._attr_unique_id = f"{DOMAIN}_current_day_type"

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

    def _current_day_context(self):
        """Return the current resolved day context."""

        today = dt_util.now().date()

        return self._runtime.resolver.resolve_day_context(today)

    @property
    def native_value(
        self,
    ) -> str | None:
        """Return the current day type name."""

        context = self._current_day_context()

        if context.day_type is None:
            return None

        return context.day_type.name

    @property
    def extra_state_attributes(
        self,
    ) -> dict:
        """Return current day type information."""

        context = self._current_day_context()

        attributes = {
            **integration_attributes(),
            "date": context.date.isoformat(),
            "cycle_id": context.cycle_id,
            "week_schedule_id": context.week_schedule_id,
            "calendar_exception_id": context.calendar_exception_id,
            "day_type_id": (
                context.day_type.id if context.day_type is not None else None
            ),
        }

        return attributes


class DayPlannerCurrentMomentSensor(SensorEntity):
    """Sensor exposing the current Day Planner moment."""

    _attr_has_entity_name = False
    _attr_name = f"{INTEGRATION_NAME} Current moment"

    def __init__(
        self,
        runtime: DayPlannerRuntimeData,
    ) -> None:
        """Initialize sensor."""

        self._runtime = runtime
        self._attr_unique_id = f"{DOMAIN}_current_moment"

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

    def _current_moment(self):
        """Return the current moment event."""

        now = dt_util.now()

        return self._runtime.scheduler.current_moment(now)

    @property
    def native_value(
        self,
    ) -> str | None:
        """Return the current moment name."""

        event = self._current_moment()

        if event is None:
            return None

        return event.moment.name

    @property
    def extra_state_attributes(
        self,
    ) -> dict:
        """Return current moment information."""

        event = self._current_moment()

        if event is None:
            return {}

        attributes = {
            **integration_attributes(),
            "moment_id": event.moment.id,
            "scheduled_at": event.scheduled_at.isoformat(),
        }

        return attributes
