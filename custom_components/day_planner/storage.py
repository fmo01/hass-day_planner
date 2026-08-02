from homeassistant.helpers.storage import Store

from .const import (
    STORAGE_VERSION,
    STORAGE_KEY,
)


class DayPlannerStorage:

    def __init__(self, hass):

        self.store = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )


    async def async_load(self):

        data = await self.store.async_load()

        if data is None:
            return {
                "moments": [],
                "day_types": [],
                "cycle": {},
                "exceptions": [],
            }

        return data


    async def async_save(self, data):

        await self.store.async_save(data)
