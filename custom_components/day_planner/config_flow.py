from homeassistant import config_entries

from .const import DOMAIN, NAME
from .options_flow import DayPlannerOptionsFlow


class DayPlannerConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle Day Planner configuration."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input=None,
    ):
        """Handle setup."""

        await self.async_set_unique_id(DOMAIN)

        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=NAME,
            data={},
        )

    @staticmethod
    def async_get_options_flow(
        config_entry,
    ):
        return DayPlannerOptionsFlow()
