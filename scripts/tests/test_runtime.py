import asyncio
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientConnectionError, ContentTypeError, RequestInfo
from homeassistant.core import HomeAssistant

from custom_components.day_planner.location import (
    DayPlannerLocation,
    LocationResult,
    LocationStatus,
    _parse_response,
)
from custom_components.day_planner.runtime import DayPlannerRuntimeData


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
    assert runtime.location is None


@pytest.fixture
def location_request():
    hass = MagicMock()
    hass.config.country = "FR"
    hass.config.latitude = 48.58
    hass.config.longitude = 7.75
    hass.states.get.return_value = None
    hass.async_add_executor_job = AsyncMock(side_effect=lambda fn, *args: fn(*args))
    response = MagicMock(status=200)
    response.json = AsyncMock(
        return_value={
            "features": [
                {
                    "properties": {
                        "countrycode": "FR",
                        "country": "France",
                        "state": "Grand Est",
                        "county": "Bas-Rhin",
                        "city": "Strasbourg",
                    }
                }
            ]
        }
    )
    session = MagicMock()
    session.get.return_value.__aenter__ = AsyncMock(return_value=response)
    session.get.return_value.__aexit__ = AsyncMock(return_value=False)
    with (
        patch(
            "custom_components.day_planner.location.async_get_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.day_planner.location.Store",
            return_value=SimpleNamespace(async_load=AsyncMock(return_value=None), async_save=AsyncMock()),
        ),
    ):
        yield DayPlannerLocation(hass), hass, response, session


def test_location_cache_survives_ha_restart(tmp_path):
    async def run():
        async def evaluate(request, longitude=7.75):
            hass = HomeAssistant(str(tmp_path))
            hass.config.country = "FR"
            hass.config.latitude, hass.config.longitude = 48.58, longitude
            location = DayPlannerLocation(hass)
            try:
                with patch.object(location, "_async_request", request):
                    await location.async_evaluate()
                return location.result
            finally:
                await hass.async_stop()

        request = AsyncMock(
            return_value=LocationResult(
                LocationStatus.RESOLVED,
                country_code="FR",
                country_name="France",
                subdivision_code="FR-67",
                subdivision_name="Bas-Rhin",
                subdivisions=(("FR-67", "Bas-Rhin"),),
                locality="Strasbourg",
            )
        )
        first = await evaluate(request)
        path = tmp_path / ".storage" / "day_planner_location"
        raw = path.read_bytes()
        data = json.loads(raw)["data"]
        assert data["home"] == ["FR", 48.58, 7.75]
        assert data["source"] == first.source
        assert data["attribution"] == first.attribution
        cached = await evaluate(request)
        request.assert_awaited_once()
        assert cached.from_cache and cached.resolved_at == first.resolved_at
        assert cached.subdivisions == first.subdivisions
        assert cached.locality == first.locality

        request.return_value = LocationResult(LocationStatus.UNRESOLVED, reason="request_failed")
        changed = await evaluate(request, longitude=8)
        assert changed.reason == "request_failed"
        request.assert_awaited_with("FR", 48.58, 8)
        assert path.read_bytes() == raw

    asyncio.run(run())


@pytest.mark.parametrize(
    "changes",
    [
        {"resolved_at": "2026-10-12T12:00:00+00:00"},
        {"resolved_at": "2026-11-12T12:00:00+00:00"},
        {"resolved_at": "2026-11-10T12:00:00"},
        {"resolved_at": "invalid"},
        {"country_code": "DE"},
        {"subdivisions": [["DE-BY", "Bayern"]]},
        {"home": ["DE", 48.58, 7.75]},
    ],
)
def test_location_replaces_invalid_disk_cache(location_request, changes):
    async def run():
        location, _, _, session = location_request
        location._store.async_load.return_value = {
            "home": ["FR", 48.58, 7.75],
            "resolved_at": "2026-11-10T12:00:00+00:00",
            "country_code": "FR",
            "subdivisions": [["FR-67", "Bas-Rhin"]],
            **changes,
        }
        with patch(
            "custom_components.day_planner.location.dt_util.utcnow",
            return_value=datetime(2026, 11, 11, 12, tzinfo=UTC),
        ):
            await location.async_evaluate()
        assert session.get.call_count == 1
        assert not location._result.from_cache
        location._store.async_save.assert_awaited_once()

    asyncio.run(run())


def test_location_keeps_working_when_storage_fails(location_request):
    async def run():
        location, _, _, session = location_request
        location._store.async_load.side_effect = OSError
        location._store.async_save.side_effect = OSError
        await location.async_evaluate()
        await location.async_evaluate()
        assert location.result.status == LocationStatus.RESOLVED
        assert location.result.from_cache
        assert session.get.call_count == 1

    asyncio.run(run())


def test_location_drops_stale_disk_read(location_request):
    async def run():
        location, hass, _, session = location_request

        async def move_during_read():
            hass.config.longitude = 8

        location._store.async_load.side_effect = move_during_read
        await location.async_evaluate()
        assert location.result is None
        session.get.assert_not_called()
        location._store.async_save.assert_not_awaited()

    asyncio.run(run())


def test_location_serializes_writes_across_home_changes(location_request):
    async def run():
        location, hass, _, _ = location_request
        location._entry = MagicMock()
        location._entry.async_create_background_task.side_effect = lambda hass, coroutine, name: asyncio.create_task(
            coroutine
        )
        started, release = asyncio.Event(), asyncio.Event()
        written = []

        async def save(data):
            if data["home"][2] == 7.75:
                started.set()
                await release.wait()
            written.append(data["home"][2])

        location._store.async_save.side_effect = save
        location._queue_evaluation()
        first = location._task
        await started.wait()
        hass.config.longitude = 8
        location._home_changed(None)
        await asyncio.sleep(0)
        assert location.result is None
        assert not written
        release.set()
        await location._task
        assert first.cancelled()
        assert written == [7.75, 8]
        location.stop()

    asyncio.run(run())


def test_location_renewal_and_retry_lifecycle(location_request):
    async def run():
        location, hass, response, _ = location_request
        location._entry = MagicMock()
        location._entry.async_create_background_task.side_effect = lambda hass, coroutine, name: asyncio.create_task(
            coroutine
        )
        now = datetime(2026, 11, 11, 12, tzinfo=UTC)
        with patch("custom_components.day_planner.location.dt_util.utcnow", return_value=now) as utcnow:
            await location.async_evaluate()
            assert hass.loop.call_later.call_args.args[0] == 30 * 86400
            renewal = location._timer
            utcnow.return_value = now + timedelta(days=30)
            assert location.result is None
            response.status = 503
            hass.loop.call_later.call_args.args[1]()
            await location._task
            renewal.cancel.assert_called()
            assert location.result.reason == "http_error"
            assert hass.loop.call_later.call_args.args[0] == 3600
            location._store.async_save.assert_awaited_once()

            response.status = 200
            hass.loop.call_later.call_args.args[1]()
            await location._task
            assert location.result.status == LocationStatus.RESOLVED
            assert location.result.resolved_at == utcnow.return_value
            response.json.return_value = {"features": []}
            hass.config.latitude = 49
            await location.async_evaluate()
            assert location.result.reason == "no_result"
            assert location._timer is None
            location.stop()

    asyncio.run(run())


@pytest.mark.parametrize(
    ("country", "state", "expected"),
    [
        ("FR", "Bas-Rhin", "FR-67"),
        ("DE", "Bayern", "DE-BY"),
        ("CH", "Genève", "CH-GE"),
        ("US", "California", "US-CA"),
        ("BE", "Liège", "BE-WLG"),
        ("AU", "Queensland", "AU-QLD"),
        ("CA", "Québec", "CA-QC"),
        ("JP", "JP-13", "JP-13"),
    ],
)
def test_location_international(country, state, expected):
    data = {"features": [{"properties": {"countrycode": country.lower(), "state": state}}]}
    result = _parse_response(data, country)
    assert result.status == LocationStatus.RESOLVED
    assert result.country_code == country
    assert result.subdivision_code == expected
    assert result.locality is None


@pytest.mark.parametrize(
    ("data", "country", "reason"),
    [
        ([], "FR", "invalid_response"),
        ({}, "FR", "invalid_response"),
        ({"features": None}, "FR", "invalid_response"),
        ({"features": []}, "FR", "no_result"),
        ({"features": [None]}, "FR", "invalid_response"),
        ({"features": [{"properties": []}]}, "FR", "invalid_response"),
        ({"features": [{"properties": {}}]}, "FR", "unknown_country"),
        (
            {"features": [{"properties": {"countrycode": "XX"}}]},
            "XX",
            "unknown_country",
        ),
        (
            {"features": [{"properties": {"countrycode": "DE"}}]},
            "FR",
            "country_mismatch",
        ),
        (
            {"features": [{"properties": {"countrycode": "FR", "state": "Uncertain"}}]},
            "FR",
            "subdivision_not_resolved",
        ),
        (
            {"features": [{"properties": {"countrycode": "FR"}}]},
            "FR",
            "subdivision_not_resolved",
        ),
    ],
)
def test_location_invalid_response(data, country, reason):
    result = _parse_response(data, country)
    assert result.status != LocationStatus.RESOLVED
    assert result.reason == reason


def test_location_administrative_ambiguity():
    data = {"features": [{"properties": {"countrycode": "US", "state": state}} for state in ("California", "Nevada")]}
    assert _parse_response(data, "US").reason == "ambiguous_location"


def test_location_duplicate_areas_are_consistent():
    data = {"features": [{"properties": {"countrycode": "DE", "county": "Bayern", "state": "Bayern"}}] * 2}
    result = _parse_response(data, None)
    assert result.status == LocationStatus.RESOLVED
    assert len(result.subdivisions) == 1


def test_location_ambiguous_iso_name():
    import pycountry

    subdivisions = [
        SimpleNamespace(code="XX-A", name="Same"),
        SimpleNamespace(code="XX-B", name="Same"),
    ]
    with patch.object(pycountry.subdivisions, "get", return_value=subdivisions):
        result = _parse_response({"features": [{"properties": {"countrycode": "DE", "state": "Same"}}]}, "DE")
    assert result.reason == "ambiguous_subdivision"


def test_location_country_without_subdivision():
    result = _parse_response(
        {"features": [{"properties": {"countrycode": "VA", "locality": "Vatican"}}]},
        None,
    )
    assert result.status == LocationStatus.RESOLVED
    assert result.locality == "Vatican"


def test_location_evaluation_and_memory_cache(location_request):
    async def run():
        location, hass, _, session = location_request
        assert location.result is None
        await location.async_evaluate()
        first = location.result
        assert first.status == LocationStatus.RESOLVED
        assert first.country_name == "France"
        assert first.subdivision_code == "FR-67"
        assert first.locality == "Strasbourg"
        assert first.last_evaluated.tzinfo is not None
        assert first.from_cache is False
        await location.async_evaluate()
        assert location.result.from_cache is True
        assert location.result.resolved_at == first.resolved_at
        assert location.result.last_evaluated >= first.last_evaluated
        assert session.get.call_count == 1
        assert session.get.call_args.args == ("https://photon.komoot.io/reverse",)
        assert session.get.call_args.kwargs["timeout"].total == 10
        assert session.get.call_args.kwargs["allow_redirects"] is False
        assert "DayPlanner" in session.get.call_args.kwargs["headers"]["User-Agent"]
        hass.config.country = "DE"
        assert location.result is None

    asyncio.run(run())


@pytest.mark.parametrize(
    ("country", "latitude", "longitude", "reason"),
    [
        ("FR", None, 7, "invalid_coordinates"),
        ("FR", 91, 7, "invalid_coordinates"),
        ("FR", -91, 7, "invalid_coordinates"),
        ("FR", 48, 181, "invalid_coordinates"),
        ("FR", 48, -181, "invalid_coordinates"),
        ("FR", True, 7, "invalid_coordinates"),
        ("FR", "48", 7, "invalid_coordinates"),
        ("FR", float("nan"), 7, "invalid_coordinates"),
        ("FR", 48, float("inf"), "invalid_coordinates"),
        ("France", 48, 7, "invalid_country"),
    ],
)
def test_location_invalid_source(location_request, country, latitude, longitude, reason):
    async def run():
        location, hass, _, session = location_request
        hass.config.country, hass.config.latitude, hass.config.longitude = (
            country,
            latitude,
            longitude,
        )
        await location.async_evaluate()
        assert location.result.reason == reason
        assert location.result.last_evaluated is not None
        assert location.result.resolved_at is None
        session.get.assert_not_called()

    asyncio.run(run())


def test_location_missing_country_and_home_zone(location_request):
    async def run():
        location, hass, _, session = location_request
        hass.config.country = None
        hass.states.get.return_value = MagicMock(attributes={"latitude": 0, "longitude": 0})
        await location.async_evaluate()
        assert location.result.country_code == "FR"
        assert session.get.call_args.kwargs["params"]["lat"] == 0
        assert session.get.call_args.kwargs["params"]["lon"] == 0

    asyncio.run(run())


@pytest.mark.parametrize("error", [TimeoutError(), ClientConnectionError(), ValueError()])
def test_location_network_error(location_request, error):
    async def run():
        location, _, _, session = location_request
        session.get.return_value.__aenter__.side_effect = error
        await location.async_evaluate()
        assert location.result.reason == "request_failed"

    asyncio.run(run())


@pytest.mark.parametrize("status", [301, 404, 429, 503])
def test_location_http_error(location_request, status):
    async def run():
        location, _, response, _ = location_request
        response.status = status
        await location.async_evaluate()
        assert location.result.reason == "http_error"
        response.json.assert_not_awaited()

    asyncio.run(run())


def test_location_bad_json(location_request):
    async def run():
        location, _, response, _ = location_request
        response.json.side_effect = ContentTypeError(MagicMock(spec=RequestInfo), ())
        await location.async_evaluate()
        assert location.result.reason == "request_failed"

    asyncio.run(run())


def test_location_stale_request_ignored(location_request):
    async def run():
        location, hass, response, _ = location_request
        data = response.json.return_value

        async def changed():
            hass.config.longitude = 8
            return data

        response.json.side_effect = changed
        await location.async_evaluate()
        assert location.result is None

    asyncio.run(run())


def test_location_cancellation_and_stop(location_request):
    async def run():
        location, _, response, _ = location_request
        response.json.side_effect = asyncio.CancelledError
        with pytest.raises(asyncio.CancelledError):
            await location.async_evaluate()
        location.stop()
        await location.async_evaluate()
        assert location.result is None

    asyncio.run(run())


def test_location_stop_during_request(location_request):
    async def run():
        location, _, response, _ = location_request
        data = response.json.return_value

        async def stopped():
            location.stop()
            return data

        response.json.side_effect = stopped
        await location.async_evaluate()
        assert location.result is None

    asyncio.run(run())


def test_location_lifecycle(location_request):
    async def run():
        location, hass, _, session = location_request
        entry = MagicMock()

        def background(hass, coroutine, name):
            return asyncio.create_task(coroutine)

        entry.async_create_background_task.side_effect = background
        with patch("custom_components.day_planner.location.async_track_state_change_event") as track:
            location.start(entry)
            await location._task
            entry.async_on_unload.assert_called_once_with(location.stop)
            track.assert_called_once()
            task = location._task
            location._home_changed(None)
            assert location._task is task
            hass.config.latitude = 49
            location._home_changed(None)
            assert location.result is None
            await location._task
            assert session.get.call_count == 2
            location.stop()
            track.return_value.assert_called_once_with()
            hass.bus.async_listen.return_value.assert_called_once_with()
            location.stop()

    asyncio.run(run())


def _calendar_location(country="FR", subdivision="FR-75C", subdivisions=()):
    return LocationResult(
        LocationStatus.RESOLVED,
        country_code=country,
        subdivision_code=subdivision,
        subdivisions=subdivisions,
    )


def test_public_holidays_france_reference_dates():
    """2026 civil dates: https://www.service-public.gouv.fr/particuliers/vosdroits/F24496."""
    from datetime import date

    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, _calendar_location(), "fr")
    assert result.status == "ready" and result.subdivision is None
    assert {day.date for day in result.days} == {
        date(2026, 1, 1),
        date(2026, 4, 6),
        date(2026, 5, 1),
        date(2026, 5, 8),
        date(2026, 5, 14),
        date(2026, 5, 25),
        date(2026, 7, 14),
        date(2026, 8, 15),
        date(2026, 11, 1),
        date(2026, 11, 11),
        date(2026, 12, 25),
    }
    assert all(day.scope == "national" for day in result.days)


@pytest.mark.parametrize(
    ("year", "good_friday"),
    [(2026, "2026-04-03"), (2027, "2027-03-26"), (2028, "2028-04-14")],
)
@pytest.mark.parametrize(
    ("code", "subdivision"),
    [("FR-57", "57"), ("FR-67", "6AE"), ("FR-68", "6AE"), ("FR-6AE", "6AE")],
)
def test_public_holidays_alsace_moselle(year, good_friday, code, subdivision):
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(year, _calendar_location(subdivision=code), "fr")
    assert result.status == "ready" and result.subdivision == subdivision
    days = {day.date.isoformat(): day for day in result.days}
    assert days[good_friday].warnings == ("local_applicability_unverified",)
    assert days[f"{year}-12-26"].scope == "regional"
    assert not days[f"{year}-12-26"].warnings
    assert days[f"{year}-12-25"].scope == "national"


@pytest.mark.parametrize(
    ("country", "code", "subdivision", "expected"),
    [
        ("DE", "DE-BY", "BY", "2026-01-06"),
        ("CH", "CH-GE", "GE", "2026-12-31"),
        ("US", "US-CA", "CA", "2026-07-04"),
        ("CA", "CA-QC", "QC", "2026-06-24"),
        ("AU", "AU-QLD", "QLD", "2026-01-26"),
        ("GB", "GB-YOR", "ENG", "2026-12-25"),
        ("VA", None, None, "2026-12-25"),
    ],
)
def test_public_holidays_international(country, code, subdivision, expected):
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, _calendar_location(country, code), "en")
    assert result.status == "ready"
    assert result.country_code == country and result.subdivision == subdivision
    assert expected in {day.date.isoformat() for day in result.days}


def test_public_holidays_coincident_names_and_observed_dates():
    from datetime import date

    from custom_components.day_planner.public_holidays import calculate_public_holidays

    french = calculate_public_holidays(2008, _calendar_location(), "fr")
    coincident = next(day for day in french.days if day.date == date(2008, 5, 1))
    assert len(coincident.names) == 2
    for year in [2021, 2022, 2027]:
        usa = calculate_public_holidays(year, _calendar_location("US", "US-CA"), "en")
        dates = {day.date for day in usa.days}
        assert all(day.year == year for day in dates)
        assert date(year, 7, 4) in dates
        if year == 2027:
            assert date(2027, 7, 5) in dates


@pytest.mark.parametrize("language", ["fr", "fr-CA", "en", "en-US", "de", "zz"])
def test_public_holidays_language(language):
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, _calendar_location(), language)
    assert result.language == ("en_US" if language.startswith("en") else "fr")
    assert result.days


@pytest.mark.parametrize("year", [True, None, "2026", 0, 10000])
def test_public_holidays_invalid_year(year):
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    assert calculate_public_holidays(year, _calendar_location(), "fr").reason == "invalid_year"


@pytest.mark.parametrize(
    ("location", "reason"),
    [
        (None, "location_unresolved"),
        (LocationResult(LocationStatus.UNRESOLVED), "location_unresolved"),
        (
            LocationResult(LocationStatus.UNRESOLVED, country_code="FR", reason="country_mismatch"),
            "location_unresolved",
        ),
        (_calendar_location("XX", None), "country_not_supported"),
    ],
)
def test_public_holidays_unavailable(location, reason):
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, location, "fr")
    assert result.reason == reason and not result.days


@pytest.mark.parametrize(
    ("location", "reason"),
    [
        (_calendar_location("US", None), "subdivision_missing"),
        (_calendar_location("US", "US-INVALID"), "subdivision_not_supported"),
        (
            _calendar_location("US", "US-CA", (("US-NV", "Nevada"),)),
            "ambiguous_subdivision",
        ),
        (_calendar_location("FR", "FR-GES"), "subdivision_not_supported"),
        (_calendar_location("FR", "US-CA"), "subdivision_not_supported"),
        (
            LocationResult(
                LocationStatus.UNRESOLVED,
                country_code="DE",
                reason="subdivision_not_resolved",
            ),
            "subdivision_missing",
        ),
    ],
)
def test_public_holidays_partial_calendar(location, reason):
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, location, "fr")
    assert result.status == "partial" and result.reason == reason
    assert result.days and result.subdivision is None


def test_public_holidays_regular_fr_department_and_duplicate_ancestors():
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    location = _calendar_location("FR", "FR-54", (("FR-GES", "Grand Est"),))
    assert calculate_public_holidays(2026, location, "fr").status == "ready"
    location = _calendar_location("FR", "FR-67", (("FR-6AE", "Alsace"), ("FR-GES", "Grand Est")))
    assert calculate_public_holidays(2026, location, "fr").subdivision == "6AE"


def test_public_holidays_limits_and_calculation_error():
    import holidays

    from custom_components.day_planner.public_holidays import calculate_public_holidays

    assert calculate_public_holidays(2101, _calendar_location(), "fr").reason == "year_not_supported"
    assert calculate_public_holidays(1700, _calendar_location(), "fr").reason == "year_not_supported"
    factory = holidays.country_holidays
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise ValueError("injected failure")
        return factory(*args, **kwargs)

    with patch(
        "custom_components.day_planner.public_holidays.holidays.country_holidays",
        side_effect=broken,
    ):
        assert calculate_public_holidays(2026, _calendar_location(), "fr").reason == "calculation_failed"


def test_public_holidays_names_do_not_depend_on_environment():
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    with patch.dict("os.environ", {"LANGUAGE": "de", "LC_ALL": "de_DE"}):
        result = calculate_public_holidays(2026, _calendar_location(), "fr")
    assert result.days[0].names == ("Jour de l'an",)


def test_public_holidays_async_context_and_translation():
    from custom_components.day_planner.public_holidays import DayPlannerPublicHolidays

    async def run():
        hass = MagicMock()
        hass.config.language = "fr"
        hass.async_add_executor_job = AsyncMock(side_effect=lambda fn, *args: fn(*args))
        location = SimpleNamespace(result=_calendar_location(subdivision="FR-67"))
        translations = {
            "component.day_planner.exceptions.public_holidays_local_applicability_unverified.message": (
                "Application locale à vérifier"
            )
        }
        with patch(
            "custom_components.day_planner.public_holidays.async_get_translations",
            AsyncMock(return_value=translations),
        ):
            result = await DayPlannerPublicHolidays(hass, location).async_get_year(2026)
            assert result["subdivision"] == "6AE" and result["status"] == "ready"
            good_friday = next(day for day in result["days"] if day["date"] == "2026-04-03")
            assert good_friday["warning_details"] == ["Application locale à vérifier"]
            assert result["reason_detail"] is None
            location.result = _calendar_location("XX", None)
            data = await DayPlannerPublicHolidays(hass, location).async_get_year(2026)
            assert data["reason_detail"] == "country_not_supported"
            hass.async_add_executor_job.side_effect = lambda fn, *args: (
                setattr(location, "result", _calendar_location("DE", "DE-BY")) or fn(*args)
            )
            data = await DayPlannerPublicHolidays(hass, location).async_get_year(2026)
            assert data["reason"] == "location_changed" and not data["days"]

    asyncio.run(run())


def test_public_holidays_mixed_scope_and_year_filter():
    from datetime import date

    import holidays

    from custom_components.day_planner.public_holidays import calculate_public_holidays

    metadata = holidays.country_holidays("FR", years=[], expand=False)
    national = holidays.HolidayBase(expand=False)
    national[date(2026, 1, 1)] = "National"
    selected = holidays.HolidayBase(expand=False)
    selected[date(2026, 1, 1)] = "National"
    selected[date(2026, 1, 1)] = "Regional"
    selected[date(2025, 12, 31)] = "Outside year"
    with patch(
        "custom_components.day_planner.public_holidays.holidays.country_holidays",
        side_effect=[metadata, national, selected],
    ):
        result = calculate_public_holidays(2026, _calendar_location(subdivision="FR-67"), "fr")
    assert len(result.days) == 1
    assert result.days[0].scope == "mixed"
    assert set(result.days[0].names) == {"National", "Regional"}


def test_public_holidays_explicit_language_with_no_catalog():
    from custom_components.day_planner.public_holidays import _calendar_language

    metadata = SimpleNamespace(default_language=None, supported_languages=())
    assert _calendar_language("zz", metadata) == "en_US"


def test_public_holidays_supported_local_calendar():
    from datetime import date

    from custom_components.day_planner.public_holidays import calculate_public_holidays

    location = LocationResult(
        LocationStatus.RESOLVED,
        country_code="DE",
        subdivision_code="DE-BY",
        locality="Augsburg",
    )
    result = calculate_public_holidays(2026, location, "de")
    assert result.subdivision == "Augsburg"
    assert date(2026, 8, 8) in {day.date for day in result.days}


def test_public_holidays_sweden_excludes_ordinary_sunday():
    """Regression documented in Home Assistant 2026.11's Holiday/Workday changes."""
    from datetime import date

    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, _calendar_location("SE", "SE-AB"), "sv")
    dates = {day.date for day in result.days}
    assert date(2026, 1, 4) not in dates
    assert date(2026, 4, 5) in dates


def test_public_holidays_belgium_community_not_inferred_from_province():
    from custom_components.day_planner.public_holidays import calculate_public_holidays

    result = calculate_public_holidays(2026, _calendar_location("BE", "BE-WLG"), "fr")
    assert result.status == "partial"
    assert result.reason == "subdivision_not_supported"
    assert result.subdivision is None
    assert "2026-07-21" in {day.date.isoformat() for day in result.days}


def test_location_and_holidays_across_years_then_move_offline(location_request):
    """Changing year reuses location; moving offline must not expose old holidays."""
    from custom_components.day_planner.public_holidays import DayPlannerPublicHolidays

    async def run():
        location, hass, _, session = location_request
        hass.config.language = "fr"
        with patch(
            "custom_components.day_planner.public_holidays.async_get_translations",
            AsyncMock(return_value={}),
        ):
            await location.async_evaluate()
            holidays = DayPlannerPublicHolidays(hass, location)
            for year in (2026, 2027, 2028):
                result = await holidays.async_get_year(year)
                assert result["status"] == "ready"
                assert result["subdivision"] == "6AE"
                assert all(day["date"].startswith(str(year)) for day in result["days"])
                assert any(day["date"] == f"{year}-12-26" for day in result["days"])
            assert session.get.call_count == 1
            hass.config.longitude = 2.35
            session.get.return_value.__aenter__.side_effect = ClientConnectionError()
            await location.async_evaluate()
            result = await holidays.async_get_year(2027)
            assert result["status"] == "unavailable"
            assert not result["days"]
            assert session.get.call_count == 2
            location.stop()

    asyncio.run(run())
