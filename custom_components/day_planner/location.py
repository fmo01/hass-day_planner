"""Resolve and expose the HA home location, independently of calendar rules."""

import asyncio
import logging
import re
import unicodedata
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum

import pycountry
from aiohttp import ClientError, ClientTimeout
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import SIGNAL_LOCATION_UPDATED

_LOGGER = logging.getLogger(__name__)
_ENDPOINT = "https://photon.komoot.io/reverse"
_SOURCE = "Photon / OpenStreetMap"
_ATTRIBUTION = "© OpenStreetMap contributors — https://www.openstreetmap.org/copyright"
_CACHE_KEY = "day_planner_location"
_CACHE_TTL = timedelta(days=30)
_RETRY_DELAY = timedelta(hours=1)


class LocationStatus(StrEnum):
    """Geographic resolution status, separate from calendar support."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class LocationResult:
    """Human-readable location and ISO codes, with evaluation provenance."""

    status: LocationStatus
    country_code: str | None = None
    country_name: str | None = None
    subdivision_code: str | None = None
    subdivision_name: str | None = None
    locality: str | None = None
    subdivisions: tuple[tuple[str, str], ...] = ()
    reason: str | None = None
    source: str = _SOURCE
    attribution: str = _ATTRIBUTION
    last_evaluated: datetime | None = None
    resolved_at: datetime | None = None
    from_cache: bool = False


def _text(value):
    """Return meaningful strings only."""
    return value.strip() if isinstance(value, str) and value.strip() else None


def _normalized(value):
    """Compare names exactly after case, accents and punctuation normalization."""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(c for c in decomposed if c.isalnum() and not unicodedata.combining(c))


def _coordinate(value, lower, upper):
    """Accept finite numeric coordinates, including zero, without coercion."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if lower <= value <= upper else None


def _fresh(resolved_at, now):
    return resolved_at is not None and timedelta(0) <= now - resolved_at < _CACHE_TTL


def _cache_result(data, key, now):
    """Validate the stored resolution before treating it as a cache hit."""
    if not isinstance(data, dict) or data.get("home") != list(key):
        return None
    try:
        resolved_at = datetime.fromisoformat(data["resolved_at"])
        country = data["country_code"]
        subdivisions = data["subdivisions"]
        if (
            resolved_at.utcoffset() is None
            or not _fresh(resolved_at, now)
            or not isinstance(country, str)
            or re.fullmatch(r"[A-Z]{2}", country) is None
            or (key[0] and country != key[0])
            or not isinstance(subdivisions, list)
            or any(
                not isinstance(item, list)
                or len(item) != 2
                or not isinstance(item[0], str)
                or not item[0].startswith(country + "-")
                or _text(item[1]) is None
                for item in subdivisions
            )
        ):
            return None
    except KeyError, TypeError, ValueError, OverflowError:
        return None
    code, name = subdivisions[0] if subdivisions else (None, None)
    return LocationResult(
        LocationStatus.RESOLVED,
        country_code=country,
        country_name=_text(data.get("country_name")),
        subdivision_code=code,
        subdivision_name=name,
        locality=_text(data.get("locality")),
        subdivisions=tuple(tuple(item) for item in subdivisions),
        source=_text(data.get("source")) or _SOURCE,
        attribution=_text(data.get("attribution")) or _ATTRIBUTION,
        resolved_at=resolved_at,
        from_cache=True,
    )


def _parse_response(data, configured_country):
    """Normalize Photon data using ISO databases; run outside the event loop."""
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        return LocationResult(LocationStatus.UNRESOLVED, reason="invalid_response")
    features = data["features"]
    if not features:
        return LocationResult(LocationStatus.UNRESOLVED, reason="no_result")
    candidates = []
    for feature in features:
        properties = feature.get("properties") if isinstance(feature, dict) else None
        if not isinstance(properties, dict):
            return LocationResult(LocationStatus.UNRESOLVED, reason="invalid_response")
        code = _text(properties.get("countrycode"))
        country = pycountry.countries.get(alpha_2=code.upper()) if code else None
        if country is None:
            return LocationResult(LocationStatus.UNSUPPORTED, reason="unknown_country")
        if configured_country and configured_country != country.alpha_2:
            return LocationResult(LocationStatus.UNRESOLVED, reason="country_mismatch")
        subdivisions = pycountry.subdivisions.get(country_code=country.alpha_2) or ()
        matches = []
        for field in ("county", "state", "region"):
            name = _text(properties.get(field))
            if name is None:
                continue
            # Accept exact ISO codes or exact normalized names, never fuzzy guesses.
            found = {
                item.code: item
                for item in subdivisions
                if name.upper() == item.code or _normalized(name) == _normalized(item.name)
            }
            if len(found) > 1:
                return LocationResult(LocationStatus.UNRESOLVED, reason="ambiguous_subdivision")
            if found:
                item = next(iter(found.values()))
                if (item.code, item.name) not in matches:
                    matches.append((item.code, item.name))
        code, name = matches[0] if matches else (None, _text(properties.get("state")))
        locality = _text(properties.get("city")) or _text(properties.get("locality"))
        candidates.append(
            LocationResult(
                (LocationStatus.RESOLVED if matches or not subdivisions else LocationStatus.UNRESOLVED),
                country_code=country.alpha_2,
                country_name=_text(properties.get("country")) or country.name,
                subdivision_code=code,
                subdivision_name=name,
                locality=locality,
                subdivisions=tuple(matches),
                reason=(None if matches or not subdivisions else "subdivision_not_resolved"),
            )
        )
    # Nearby objects can differ in locality; conflicting administrative areas are unsafe.
    if len({(r.country_code, r.subdivisions, r.subdivision_name) for r in candidates}) != 1:
        return LocationResult(LocationStatus.UNRESOLVED, reason="ambiguous_location")
    return candidates[0]


class DayPlannerLocation:
    """Resolve the HA home and maintain a cache of the last successful lookup."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._result = None
        self._source_key = None
        self._stopped = False
        self._task = None
        self._entry = None
        self._unsubscribers = []
        self._lock = asyncio.Lock()
        self._store = Store(hass, 1, _CACHE_KEY, private=True, atomic_writes=True)
        self._timer = None

    def _home_source(self):
        country = _text(self.hass.config.country)
        country = country.upper() if country else None
        latitude, longitude = self.hass.config.latitude, self.hass.config.longitude
        home = self.hass.states.get("zone.home")
        attributes = getattr(home, "attributes", None)
        if isinstance(attributes, dict) and "latitude" in attributes and "longitude" in attributes:
            latitude, longitude = attributes["latitude"], attributes["longitude"]
        return (
            country,
            _coordinate(latitude, -90, 90),
            _coordinate(longitude, -180, 180),
        )

    @property
    def result(self) -> LocationResult | None:
        """Never expose a cached location for a changed home."""
        if self._stopped or self._source_key != self._home_source():
            return None
        if (
            self._result
            and self._result.status == LocationStatus.RESOLVED
            and not _fresh(self._result.resolved_at, dt_util.utcnow())
        ):
            return None
        return self._result

    async def async_evaluate(self) -> None:
        """Evaluate the current home using memory, disk, or the geocoder."""
        async with self._lock:
            if self._stopped:
                return
            key = self._home_source()
            country, latitude, longitude = key
            cached = self.result
            if cached and cached.status == LocationStatus.RESOLVED:
                result = replace(cached, from_cache=True)
            elif latitude is None or longitude is None:
                result = LocationResult(
                    LocationStatus.UNRESOLVED,
                    country_code=country,
                    reason="invalid_coordinates",
                )
            elif country and re.fullmatch(r"[A-Z]{2}", country) is None:
                result = LocationResult(LocationStatus.UNRESOLVED, reason="invalid_country")
            else:
                try:
                    data = await self._store.async_load()
                except (
                    HomeAssistantError,
                    KeyError,
                    NotImplementedError,
                    OSError,
                    TypeError,
                    ValueError,
                ):
                    _LOGGER.warning("Could not read the Day Planner location cache")
                    data = None
                if self._stopped or key != self._home_source():
                    return
                result = _cache_result(data, key, dt_util.utcnow())
                if result is None:
                    result = await self._async_request(country, latitude, longitude)
            if self._stopped or key != self._home_source():
                return
            now = dt_util.utcnow()
            if result.status == LocationStatus.RESOLVED and not result.from_cache:
                result = replace(result, resolved_at=now)
            self._result = replace(result, last_evaluated=now)
            self._source_key = key
            async_dispatcher_send(self.hass, SIGNAL_LOCATION_UPDATED)
            self._schedule_next(result, now)
            if result.status == LocationStatus.RESOLVED and not result.from_cache:
                write = asyncio.create_task(self._async_save(key, result))
                try:
                    await asyncio.shield(write)
                except asyncio.CancelledError:
                    # Keep the evaluation lock until the disk write finishes.
                    await write
                    raise

    async def _async_save(self, key, result) -> None:
        try:
            await self._store.async_save(
                {
                    "home": list(key),
                    "resolved_at": result.resolved_at.isoformat(),
                    "country_code": result.country_code,
                    "country_name": result.country_name,
                    "locality": result.locality,
                    "source": result.source,
                    "attribution": result.attribution,
                    "subdivisions": [list(item) for item in result.subdivisions],
                }
            )
        except HomeAssistantError, OSError:
            _LOGGER.warning("Could not save the Day Planner location cache")

    @callback
    def _schedule_next(self, result, now) -> None:
        self._cancel_timer()
        if self._entry is None:
            return
        if result.status == LocationStatus.RESOLVED:
            delay = (result.resolved_at + _CACHE_TTL - now).total_seconds()
        elif result.reason in {"request_failed", "http_error"}:
            delay = _RETRY_DELAY.total_seconds()
        else:
            return
        self._timer = self.hass.loop.call_later(max(0, delay), self._queue_evaluation)

    @callback
    def _cancel_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    async def _async_request(self, country, latitude, longitude):
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                _ENDPOINT,
                params={"lat": latitude, "lon": longitude, "limit": 2, "radius": 1},
                headers={"User-Agent": "DayPlanner/0.3.1 (https://github.com/fmo01/hass-day_planner)"},
                timeout=ClientTimeout(total=10),
                allow_redirects=False,
            ) as response:
                if response.status != 200:
                    return LocationResult(
                        LocationStatus.UNRESOLVED,
                        country_code=country,
                        reason="http_error",
                    )
                data = await response.json()
            return await self.hass.async_add_executor_job(_parse_response, data, country)
        except ClientError, TimeoutError, ValueError:
            _LOGGER.debug("Day Planner location could not be resolved")
            return LocationResult(LocationStatus.UNRESOLVED, country_code=country, reason="request_failed")

    @callback
    def start(self, entry) -> None:
        """Schedule initial evaluation and track changes of the HA home only."""
        self._entry = entry
        self._unsubscribers = [
            self.hass.bus.async_listen(EVENT_CORE_CONFIG_UPDATE, self._home_changed),
            async_track_state_change_event(self.hass, ["zone.home"], self._home_changed),
        ]
        entry.async_on_unload(self.stop)
        self._queue_evaluation()

    @callback
    def _home_changed(self, event) -> None:
        if self._source_key != self._home_source():
            async_dispatcher_send(self.hass, SIGNAL_LOCATION_UPDATED)
            self._queue_evaluation()

    @callback
    def _queue_evaluation(self) -> None:
        self._cancel_timer()
        if self._task is not None:
            self._task.cancel()
        self._task = self._entry.async_create_background_task(
            self.hass, self.async_evaluate(), "Day Planner location evaluation"
        )

    @callback
    def stop(self) -> None:
        """Cancel in-flight work and detach listeners when the entry unloads."""
        self._stopped = True
        self._cancel_timer()
        if self._task is not None:
            self._task.cancel()
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()
