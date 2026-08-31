import asyncio
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.day_planner.const import (
    DOMAIN, SERVICE_ADD_CALENDAR_EXCEPTION, SERVICE_ADD_CYCLE,
    SERVICE_ADD_DAY_TYPE, SERVICE_ADD_MOMENT, SERVICE_ADD_SCHEDULED_MOMENT,
    SERVICE_ADD_WEEK_SCHEDULE, SERVICE_REMOVE_CALENDAR_EXCEPTION,
    SERVICE_REMOVE_CYCLE, SERVICE_REMOVE_DAY_TYPE, SERVICE_REMOVE_MOMENT,
    SERVICE_REMOVE_SCHEDULED_MOMENT, SERVICE_REMOVE_WEEK_SCHEDULE,
    SERVICE_UPDATE_CALENDAR_EXCEPTION, SERVICE_UPDATE_CYCLE,
    SERVICE_UPDATE_DAY_TYPE, SERVICE_UPDATE_MOMENT,
    SERVICE_UPDATE_SCHEDULED_MOMENT, SERVICE_UPDATE_WEEK_SCHEDULE,
    SIGNAL_PLANNER_UPDATED)
from custom_components.day_planner.domain.action import Action
from custom_components.day_planner.domain.moment import Moment
from custom_components.day_planner.planner.errors import PlannerError
from custom_components.day_planner.services import (_execute, _get_runtime,
                                                    async_setup_services)


class FakeStorage:
    def __init__(self):
        self.saved_configuration = None
        self.save_count = 0

    async def async_save(self, configuration):
        self.saved_configuration = configuration
        self.save_count += 1


class FakeEngine:
    def __init__(self):
        self.configuration = object()


class FakeResolver:
    def __init__(self):
        self.configuration = None
        self.update_count = 0

    def update_configuration(
        self,
        configuration,
    ):
        self.configuration = configuration
        self.update_count += 1


class FakeHAScheduler:
    def __init__(self):
        self.schedule_count = 0

    async def async_schedule_next(self):
        self.schedule_count += 1


class FakeRuntime:
    def __init__(self):
        self.hass = MagicMock()
        self.storage = FakeStorage()
        self.engine = FakeEngine()
        self.resolver = FakeResolver()
        self.ha_scheduler = FakeHAScheduler()


def get_registered_service(
    hass,
    service_name,
):
    """Return a registered service handler by name."""

    return next(
        call.args[2]
        for call in hass.services.async_register.call_args_list
        if call.args[1] == service_name
    )


def test_execute_success():
    runtime = FakeRuntime()
    executed = False

    def operation():
        nonlocal executed
        executed = True

    with patch(
        "custom_components.day_planner.services.async_dispatcher_send"
    ) as dispatcher_send:
        asyncio.run(
            _execute(
                operation=operation,
                runtime=runtime,
                description="test operation",
            )
        )

    assert executed is True

    assert runtime.storage.save_count == 1
    assert runtime.storage.saved_configuration is runtime.engine.configuration

    assert runtime.resolver.update_count == 1
    assert runtime.resolver.configuration is runtime.engine.configuration

    assert runtime.ha_scheduler.schedule_count == 1

    dispatcher_send.assert_called_once_with(
        runtime.hass,
        SIGNAL_PLANNER_UPDATED,
    )


def test_execute_planner_error():
    runtime = FakeRuntime()

    def operation():
        raise PlannerError("Test planner error")

    with pytest.raises(
        HomeAssistantError,
        match="Test planner error",
    ):
        asyncio.run(
            _execute(
                operation=operation,
                runtime=runtime,
                description="test operation",
            )
        )

    assert runtime.storage.save_count == 0
    assert runtime.resolver.update_count == 0
    assert runtime.ha_scheduler.schedule_count == 0


def test_execute_unexpected_error():
    runtime = FakeRuntime()

    def operation():
        raise RuntimeError("Unexpected error")

    with pytest.raises(
        RuntimeError,
        match="Unexpected error",
    ):
        asyncio.run(
            _execute(
                operation=operation,
                runtime=runtime,
                description="test operation",
            )
        )

    assert runtime.storage.save_count == 0
    assert runtime.resolver.update_count == 0
    assert runtime.ha_scheduler.schedule_count == 0


def test_service_add_moment():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.add_moment = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_ADD_MOMENT,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_ADD_MOMENT,
            data={
                "id": "m2",
                "name": "Moment 2",
                "icon": "mdi:home",
                "actions": [
                    {
                        "id": "salon_on",
                        "service": "light.turn_on",
                        "data": {
                            "entity_id": "light.salon",
                            "brightness_pct": 50,
                        },
                    },
                ],
            },
        )

        await service(call)

    asyncio.run(run())

    moment = runtime.engine.add_moment.call_args.args[0]

    assert moment.id == "m2"
    assert moment.name == "Moment 2"
    assert moment.icon == "mdi:home"
    assert moment.actions == (
        Action(
            id="salon_on",
            service="light.turn_on",
            data={
                "entity_id": "light.salon",
                "brightness_pct": 50,
            },
        ),
    )

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_moment():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.update_moment = MagicMock()

    existing_action = Action(
        id="salon_on",
        service="light.turn_on",
        data={
            "entity_id": "light.salon",
        },
    )

    runtime.engine.get_moment = MagicMock(
        return_value=Moment(
            id="m1",
            name="Moment 1",
            icon="mdi:coffee",
            actions=(existing_action,),
        )
    )

    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_MOMENT,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_MOMENT,
            data={
                "id": "m1",
                "name": "Moment modifié",
                "icon": "mdi:home",
            },
        )

        await service(call)

    asyncio.run(run())

    moment = runtime.engine.update_moment.call_args.args[0]

    assert moment.id == "m1"
    assert moment.name == "Moment modifié"
    assert moment.icon == "mdi:home"
    assert moment.actions == (existing_action,)

    runtime.engine.get_moment.assert_called_once_with("m1")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_moment_clear_actions():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()

    existing_action = Action(
        id="salon_on",
        service="light.turn_on",
        data={
            "entity_id": "light.salon",
        },
    )

    runtime.engine.get_moment = MagicMock(
        return_value=Moment(
            id="m1",
            name="Moment 1",
            actions=(existing_action,),
        )
    )

    runtime.engine.update_moment = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_MOMENT,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_MOMENT,
            data={
                "id": "m1",
                "name": "Moment modifié",
                "icon": "mdi:home",
                "actions": [],
            },
        )

        await service(call)

    asyncio.run(run())

    moment = runtime.engine.update_moment.call_args.args[0]

    assert moment.id == "m1"
    assert moment.actions == ()

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_remove_moment():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.remove_moment = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_REMOVE_MOMENT,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_REMOVE_MOMENT,
            data={
                "id": "m1",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.remove_moment.assert_called_once_with("m1")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_add_day_type():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.add_day_type = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_ADD_DAY_TYPE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_ADD_DAY_TYPE,
            data={
                "id": "dt2",
                "name": "Weekend",
            },
        )

        await service(call)

    asyncio.run(run())

    day_type = runtime.engine.add_day_type.call_args.args[0]

    assert day_type.id == "dt2"
    assert day_type.name == "Weekend"
    assert day_type.scheduled_moments == ()

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_day_type():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.update_day_type = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_DAY_TYPE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_DAY_TYPE,
            data={
                "id": "dt1",
                "name": "Télétravail modifié",
            },
        )

        await service(call)

    asyncio.run(run())

    day_type = runtime.engine.update_day_type.call_args.args[0]

    assert day_type.id == "dt1"
    assert day_type.name == "Télétravail modifié"
    assert day_type.scheduled_moments == ()

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_remove_day_type():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.remove_day_type = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_REMOVE_DAY_TYPE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_REMOVE_DAY_TYPE,
            data={
                "id": "dt1",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.remove_day_type.assert_called_once_with("dt1")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_add_week_schedule():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.add_week_schedule = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_ADD_WEEK_SCHEDULE,
        )
        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_ADD_WEEK_SCHEDULE,
            data={
                "id": "ws2",
                "name": "Semaine 2",
                "monday": "dt1",
                "tuesday": "dt1",
                "wednesday": "dt1",
                "thursday": "dt1",
                "friday": "dt1",
                "saturday": "dt1",
                "sunday": "dt1",
            },
        )

        await service(call)

    asyncio.run(run())

    week_schedule = runtime.engine.add_week_schedule.call_args.args[0]

    assert week_schedule.id == "ws2"
    assert week_schedule.name == "Semaine 2"
    assert week_schedule.monday == "dt1"
    assert week_schedule.tuesday == "dt1"
    assert week_schedule.wednesday == "dt1"
    assert week_schedule.thursday == "dt1"
    assert week_schedule.friday == "dt1"
    assert week_schedule.saturday == "dt1"
    assert week_schedule.sunday == "dt1"

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_week_schedule():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.update_week_schedule = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_WEEK_SCHEDULE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_WEEK_SCHEDULE,
            data={
                "id": "ws1",
                "name": "Semaine modifiée",
                "monday": "dt2",
                "tuesday": "dt1",
                "wednesday": "dt1",
                "thursday": "dt1",
                "friday": "dt2",
                "saturday": "dt2",
                "sunday": "dt2",
            },
        )

        await service(call)

    asyncio.run(run())

    week_schedule = runtime.engine.update_week_schedule.call_args.args[0]

    assert week_schedule.id == "ws1"
    assert week_schedule.name == "Semaine modifiée"
    assert week_schedule.monday == "dt2"
    assert week_schedule.tuesday == "dt1"
    assert week_schedule.wednesday == "dt1"
    assert week_schedule.thursday == "dt1"
    assert week_schedule.friday == "dt2"
    assert week_schedule.saturday == "dt2"
    assert week_schedule.sunday == "dt2"

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_remove_week_schedule():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.remove_week_schedule = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_REMOVE_WEEK_SCHEDULE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_REMOVE_WEEK_SCHEDULE,
            data={
                "id": "ws1",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.remove_week_schedule.assert_called_once_with("ws1")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_add_cycle():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.add_cycle = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_ADD_CYCLE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_ADD_CYCLE,
            data={
                "id": "c2",
                "name": "Cycle 2",
                "start_date": "2026-08-31",
                "week_schedule_ids": ["ws1", "ws2"],
            },
        )

        await service(call)

    asyncio.run(run())

    cycle = runtime.engine.add_cycle.call_args.args[0]

    assert cycle.id == "c2"
    assert cycle.name == "Cycle 2"
    assert cycle.start_date == date(2026, 8, 31)
    assert cycle.week_schedule_ids == ("ws1", "ws2")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_cycle():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.update_cycle = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_CYCLE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_CYCLE,
            data={
                "id": "c1",
                "name": "Cycle modifié",
                "start_date": "2026-08-31",
                "week_schedule_ids": ["ws1", "ws2"],
            },
        )

        await service(call)

    asyncio.run(run())

    cycle = runtime.engine.update_cycle.call_args.args[0]

    assert cycle.id == "c1"
    assert cycle.name == "Cycle modifié"
    assert cycle.start_date == date(2026, 8, 31)
    assert cycle.week_schedule_ids == ("ws1", "ws2")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_remove_cycle():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.remove_cycle = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_REMOVE_CYCLE,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_REMOVE_CYCLE,
            data={
                "id": "c1",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.remove_cycle.assert_called_once_with("c1")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_add_calendar_exception():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.add_calendar_exception = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_ADD_CALENDAR_EXCEPTION,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_ADD_CALENDAR_EXCEPTION,
            data={
                "id": "ce2",
                "date": "15/08/2026",
                "day_type_id": "dt1",
                "description": "Férié",
            },
        )

        await service(call)

    asyncio.run(run())

    exception = runtime.engine.add_calendar_exception.call_args.args[0]

    assert exception.id == "ce2"
    assert exception.date == date(2026, 8, 15)
    assert exception.day_type_id == "dt1"
    assert exception.description == "Férié"

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_calendar_exception():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.update_calendar_exception = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_CALENDAR_EXCEPTION,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_CALENDAR_EXCEPTION,
            data={
                "id": "ce1",
                "date": "20/08/2026",
                "day_type_id": "dt2",
                "description": "Congé modifié",
            },
        )

        await service(call)

    asyncio.run(run())

    exception = runtime.engine.update_calendar_exception.call_args.args[0]

    assert exception.id == "ce1"
    assert exception.date == date(2026, 8, 20)
    assert exception.day_type_id == "dt2"
    assert exception.description == "Congé modifié"

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_remove_calendar_exception():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.remove_calendar_exception = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_REMOVE_CALENDAR_EXCEPTION,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_REMOVE_CALENDAR_EXCEPTION,
            data={
                "id": "ce1",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.remove_calendar_exception.assert_called_once_with("ce1")

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_get_runtime_not_configured():
    hass = MagicMock(spec=HomeAssistant)

    hass.config_entries.async_entries.return_value = []

    with pytest.raises(
        HomeAssistantError,
        match="Day Planner is not configured.",
    ):
        _get_runtime(hass)


def test_execute_storage_error():
    runtime = FakeRuntime()

    async def failing_save(configuration):
        raise RuntimeError("Storage failure")

    runtime.storage.async_save = failing_save

    def operation():
        pass

    with pytest.raises(
        RuntimeError,
        match="Storage failure",
    ):
        asyncio.run(
            _execute(
                operation=operation,
                runtime=runtime,
                description="test operation",
            )
        )

    assert runtime.resolver.update_count == 0
    assert runtime.ha_scheduler.schedule_count == 0


def test_service_add_scheduled_moment():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.add_scheduled_moment = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = next(
            call.args[2]
            for call in hass.services.async_register.call_args_list
            if call.args[1] == SERVICE_ADD_SCHEDULED_MOMENT
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_ADD_SCHEDULED_MOMENT,
            data={
                "day_type_id": "test_day",
                "moment_id": "test",
                "time": "17:00:00",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.add_scheduled_moment.assert_called_once()

    args = runtime.engine.add_scheduled_moment.call_args.args

    assert args[0] == "test_day"

    scheduled_moment = args[1]

    assert scheduled_moment.moment_id == "test"
    assert scheduled_moment.time_definition.fixed_time == time(
        17,
        0,
    )

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_update_scheduled_moment():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.update_scheduled_moment = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_UPDATE_SCHEDULED_MOMENT,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_UPDATE_SCHEDULED_MOMENT,
            data={
                "day_type_id": "test_day",
                "moment_id": "test",
                "time": "18:30:00",
            },
        )

        await service(call)

    asyncio.run(run())

    args = runtime.engine.update_scheduled_moment.call_args.args

    assert args[0] == "test_day"

    scheduled_moment = args[1]

    assert scheduled_moment.moment_id == "test"
    assert scheduled_moment.time_definition.fixed_time == time(18, 30)

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)


def test_service_remove_scheduled_moment():
    hass = MagicMock(spec=HomeAssistant)

    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    runtime = MagicMock()
    runtime.engine.remove_scheduled_moment = MagicMock()
    runtime.engine.configuration = object()
    runtime.storage.async_save = AsyncMock()
    runtime.resolver.update_configuration = MagicMock()
    runtime.ha_scheduler.async_schedule_next = AsyncMock()

    entry = MagicMock()
    entry.runtime_data = runtime

    hass.config_entries.async_entries.return_value = [entry]

    async def run():
        await async_setup_services(hass)

        service = get_registered_service(
            hass,
            SERVICE_REMOVE_SCHEDULED_MOMENT,
        )

        call = ServiceCall(
            hass=hass,
            domain=DOMAIN,
            service=SERVICE_REMOVE_SCHEDULED_MOMENT,
            data={
                "day_type_id": "test_day",
                "moment_id": "test",
            },
        )

        await service(call)

    asyncio.run(run())

    runtime.engine.remove_scheduled_moment.assert_called_once_with(
        "test_day",
        "test",
    )

    runtime.storage.async_save.assert_awaited_once_with(runtime.engine.configuration)
