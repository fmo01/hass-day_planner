"""Tests for the Day Planner management panel."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.day_planner.const import (CONF_SHOW_SIDEBAR_PANEL, NAME,
                                                 PANEL_COMPONENT_NAME,
                                                 PANEL_ICON, PANEL_URL_PATH)
from custom_components.day_planner.frontend import FRONTEND_URL
from custom_components.day_planner.panel import (async_setup_panel,
                                                 async_unload_panel)


@pytest.mark.parametrize(
    ("options", "sidebar_title"),
    [
        ({}, NAME),
        ({CONF_SHOW_SIDEBAR_PANEL: True}, NAME),
        ({CONF_SHOW_SIDEBAR_PANEL: False}, None),
    ],
)
def test_setup_panel_visibility(options, sidebar_title):
    async def run():
        hass = MagicMock()
        entry = MagicMock()
        entry.options = options
        with patch(
            "custom_components.day_planner.panel.panel_custom.async_register_panel",
            new_callable=AsyncMock,
        ) as register:
            await async_setup_panel(hass, entry)
            register.assert_awaited_once_with(
                hass=hass,
                webcomponent_name=PANEL_COMPONENT_NAME,
                frontend_url_path=PANEL_URL_PATH,
                sidebar_title=sidebar_title,
                sidebar_icon=PANEL_ICON,
                module_url=f"{FRONTEND_URL}/day-planner-panel.js",
                embed_iframe=False,
                require_admin=False,
            )

    asyncio.run(run())


def test_unload_panel():
    hass = MagicMock()
    with patch(
        "custom_components.day_planner.panel.frontend.async_remove_panel"
    ) as remove:
        async_unload_panel(hass)
        remove.assert_called_once_with(hass, PANEL_URL_PATH)
