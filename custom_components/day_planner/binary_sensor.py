"""Diagnostic location entity for Day Planner."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.translation import async_get_translations

from .const import DOMAIN, SIGNAL_LOCATION_UPDATED
from .integration_info import integration_attributes
from .location import LocationStatus


async def async_setup_entry(hass, entry, async_add_entities):
    """Expose the installation location independently from the planning sensors."""
    translations = await async_get_translations(hass, hass.config.language, "entity", {DOMAIN})
    async_add_entities([DayPlannerLocationSensor(entry.runtime_data.location, translations)])


class DayPlannerLocationSensor(BinarySensorEntity):
    """Whether Day Planner has a usable geographic location."""

    _attr_translation_key = "location"
    _attr_has_entity_name = True
    _attr_unique_id = f"{DOMAIN}_location"
    _attr_icon = "mdi:map-marker-check"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, location, translations):
        self._location = location
        self._translations = translations
        self.entity_id = f"binary_sensor.{DOMAIN}_location"

    @property
    def available(self):
        return self._location.result is not None

    @property
    def is_on(self):
        result = self._location.result
        return result.status == LocationStatus.RESOLVED if result else None

    @property
    def extra_state_attributes(self):
        result = self._location.result
        attributes = integration_attributes()
        if result is not None:
            attributes.update(
                {
                    "last_evaluated": (result.last_evaluated.isoformat() if result.last_evaluated else None),
                    "country_code": result.country_code,
                    "country_name": result.country_name,
                    "subdivision_code": result.subdivision_code,
                    "subdivision_name": result.subdivision_name,
                    "locality": result.locality,
                    "subdivisions": dict(result.subdivisions),
                    "source": result.source,
                    "attribution": result.attribution,
                    "from_cache": result.from_cache,
                    "resolved_at": (result.resolved_at.isoformat() if result.resolved_at else None),
                    "status": result.status.value,
                    "reason": result.reason,
                    "reason_detail": self._translations.get(
                        f"component.{DOMAIN}.entity.binary_sensor.location"
                        f".state_attributes.reason.state.{result.reason}",
                        result.reason,
                    ),
                }
            )
        return attributes

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_LOCATION_UPDATED, self._location_updated))

    @callback
    def _location_updated(self):
        self.async_write_ha_state()

    async def async_update(self):
        """Allow homeassistant.update_entity to evaluate the current home."""
        await self._location.async_evaluate()
