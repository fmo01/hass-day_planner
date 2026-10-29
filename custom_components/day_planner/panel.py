"""Day Planner management panel."""

from homeassistant.components import frontend, panel_custom
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_SHOW_SIDEBAR_PANEL,
    DEFAULT_SHOW_SIDEBAR_PANEL,
    NAME,
    PANEL_COMPONENT_NAME,
    PANEL_ICON,
    PANEL_URL_PATH,
)
from .frontend import FRONTEND_URL


async def async_setup_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register the panel; hiding the sidebar keeps direct access available."""
    show_sidebar = entry.options.get(
        CONF_SHOW_SIDEBAR_PANEL, DEFAULT_SHOW_SIDEBAR_PANEL
    )
    await panel_custom.async_register_panel(
        hass=hass,
        webcomponent_name=PANEL_COMPONENT_NAME,
        frontend_url_path=PANEL_URL_PATH,
        sidebar_title=NAME if show_sidebar else None,
        sidebar_icon=PANEL_ICON,
        module_url=f"{FRONTEND_URL}/day-planner-panel.js",
        embed_iframe=False,
        require_admin=False,
    )


def async_unload_panel(hass: HomeAssistant) -> None:
    """Remove the panel when the integration is unloaded."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
