from homeassistant import config_entries

from .const import DOMAIN, NAME


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

        await self.async_set_unique_id(
            DOMAIN
        )

        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=NAME,
            data={},
        )
