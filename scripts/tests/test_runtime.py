from unittest.mock import MagicMock

from custom_components.day_planner.runtime import (
    DayPlannerRuntimeData,
)


def test_runtime_data():
    hass = MagicMock()
    storage = MagicMock()
    engine = MagicMock()
    resolver = MagicMock()
    scheduler = MagicMock()
    action_executor = MagicMock()
    ha_scheduler = MagicMock()

    runtime = DayPlannerRuntimeData(
        hass=hass,
        storage=storage,
        engine=engine,
        resolver=resolver,
        scheduler=scheduler,
        action_executor=action_executor,
        ha_scheduler=ha_scheduler,
    )

    assert runtime.hass is hass
    assert runtime.storage is storage
    assert runtime.engine is engine
    assert runtime.resolver is resolver
    assert runtime.scheduler is scheduler
    assert runtime.action_executor is action_executor
    assert runtime.ha_scheduler is ha_scheduler
