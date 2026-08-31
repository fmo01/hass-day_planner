from custom_components.day_planner.integration_info import (
    INTEGRATION_VERSION, integration_attributes)


def test_integration_version():
    assert INTEGRATION_VERSION == "0.0.4"


def test_integration_attributes():
    assert integration_attributes() == {
        "integration": "Day Planner",
        "integration_version": "0.0.4",
        "release_url": "https://github.com/fmo01/hass-day_planner/releases",
    }
