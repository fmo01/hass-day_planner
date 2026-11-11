"""Local public holiday calculations using the HA installation's geography."""

from dataclasses import dataclass
from datetime import date as calendar_date
from datetime import timedelta

import holidays
import pycountry
from dateutil.easter import easter
from homeassistant.helpers.translation import async_get_translations

from .const import DOMAIN
from .location import LocationResult, LocationStatus


@dataclass(frozen=True)
class PublicHoliday:
    """One calendar date, preserving coincident holiday names."""

    date: calendar_date
    names: tuple[str, ...]
    scope: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class PublicHolidayYear:
    """A calendar result whose coverage is explicit."""

    year: int
    country_code: str | None = None
    subdivision: str | None = None
    language: str | None = None
    status: str = "unavailable"
    reason: str | None = "location_unresolved"
    days: tuple[PublicHoliday, ...] = ()

    def to_dict(self):
        """Return serializable data, without changing the planner."""
        return {
            "year": self.year,
            "country_code": self.country_code,
            "subdivision": self.subdivision,
            "language": self.language,
            "status": self.status,
            "reason": self.reason,
            "scope": "subdivision" if self.subdivision else "national",
            "source": "holidays",
            "source_version": holidays.__version__,
            "observed": True,
            "days": [
                {
                    "date": item.date.isoformat(),
                    "names": list(item.names),
                    "scope": item.scope,
                    "warnings": list(item.warnings),
                }
                for item in self.days
            ],
        }


def _geographic_codes(location):
    """Include ISO ancestors, preserving the most specific geographical level."""
    result = []
    codes = [location.subdivision_code] + [code for code, _ in location.subdivisions]
    for code in codes:
        while code and code not in result:
            result.append(code)
            entry = pycountry.subdivisions.get(code=code)
            code = getattr(entry, "parent_code", None)
    return result


def _calendar_subdivision(country, codes, supported, locality=None):
    """Translate geographical ISO codes into supported calendar subdivisions."""
    matches = []
    for code in codes:
        if not code.startswith(country + "-"):
            continue
        candidate = code.split("-", 1)[1]
        # holidays models the Alsace collectivity, not its two departments.
        if country == "FR" and candidate in {"67", "68"}:
            candidate = "6AE"
        if candidate in supported and candidate not in matches:
            matches.append(candidate)
    if len(matches) > 1:
        return None, "ambiguous_subdivision"
    if locality in supported and pycountry.subdivisions.get(code=f"{country}-{locality}") is None:
        return locality, None
    if matches:
        return matches[0], None
    if not supported:
        return None, None
    if country == "FR" and codes:
        # Grand Est alone does not distinguish Alsace-Moselle from other departments.
        # An identified department or collectivity can disambiguate this safely.
        entries = [pycountry.subdivisions.get(code=code) for code in codes]
        if any(entry is not None and entry.country_code == country for entry in entries) and (
            "FR-GES" not in codes
            or any(
                entry is not None
                and entry.type
                in {
                    "Metropolitan department",
                    "Metropolitan collectivity with special status",
                }
                for entry in entries
            )
        ):
            return None, None
    return None, "subdivision_not_supported" if codes else "subdivision_missing"


def _calendar_language(requested, calendar):
    """Choose an explicit supported language, without consulting process locales."""
    requested = requested.replace("-", "_")
    supported = calendar.supported_languages
    default = calendar.default_language or "en_US"
    if requested in supported:
        return requested
    base = requested.split("_")[0]
    if base in supported:
        return base
    if default.split("_")[0] == base:
        return default
    return next((language for language in supported if language.split("_")[0] == base), default)


def calculate_public_holidays(year, location: LocationResult | None, requested_language):
    """Calculate one year off the event loop; no network or planner writes."""
    if isinstance(year, bool) or not isinstance(year, int) or not 1 <= year <= 9999:
        return PublicHolidayYear(year, reason="invalid_year")
    if (
        location is None
        or not location.country_code
        or (location.status != LocationStatus.RESOLVED and location.reason != "subdivision_not_resolved")
    ):
        return PublicHolidayYear(year)
    country = location.country_code
    try:
        metadata = holidays.country_holidays(country, years=[], expand=False)
    except NotImplementedError:
        return PublicHolidayYear(year, country, status="unsupported", reason="country_not_supported")
    if not metadata.start_year <= year <= metadata.end_year:
        return PublicHolidayYear(year, country, status="unsupported", reason="year_not_supported")
    language = _calendar_language(requested_language, metadata)
    subdivision, reason = _calendar_subdivision(
        country, _geographic_codes(location), metadata.subdivisions, location.locality
    )
    try:
        national = holidays.country_holidays(country, years=[year], expand=False, observed=True, language=language)
        selected = (
            holidays.country_holidays(
                country,
                subdiv=subdivision,
                years=[year],
                expand=False,
                observed=True,
                language=language,
            )
            if subdivision
            else national
        )
    except ValueError, NotImplementedError:
        return PublicHolidayYear(year, country, subdivision, language, reason="calculation_failed")
    days = []
    for day in sorted(selected):
        if day.year != year:
            continue
        names = tuple(selected.get_list(day))
        national_names = set(national.get_list(day))
        extra_names = set(names) - national_names
        scope = "mixed" if national_names and extra_names else "national" if national_names else "regional"
        warnings = ()
        if country == "FR" and subdivision in {"57", "6AE"} and day == easter(year) - timedelta(days=2):
            warnings = ("local_applicability_unverified",)
        days.append(PublicHoliday(day, names, scope, warnings))
    return PublicHolidayYear(
        year,
        country,
        subdivision,
        language,
        "partial" if reason else "ready",
        reason,
        tuple(days),
    )


def _location_context(location):
    """Ignore evaluation timestamps, but detect a changed geographical context."""
    return (
        None
        if location is None
        else (
            location.status,
            location.country_code,
            location.subdivision_code,
            location.subdivisions,
            location.reason,
            location.locality,
        )
    )


class DayPlannerPublicHolidays:
    """Read-only access to the installation's public holiday calendar."""

    def __init__(self, hass, location):
        self.hass = hass
        self.location = location

    async def async_get_year(self, year):
        location = self.location.result
        language = self.hass.config.language
        result = await self.hass.async_add_executor_job(calculate_public_holidays, year, location, language)
        if _location_context(location) != _location_context(self.location.result):
            result = PublicHolidayYear(year, reason="location_changed")
        translations = await async_get_translations(self.hass, language, "exceptions", {DOMAIN})
        data = result.to_dict()

        def translated(code):
            if code is None:
                return None
            return translations.get(f"component.{DOMAIN}.exceptions.public_holidays_{code}.message", code)

        data["reason_detail"] = translated(result.reason)
        for day in data["days"]:
            day["warning_details"] = [translated(code) for code in day["warnings"]]
        return data
