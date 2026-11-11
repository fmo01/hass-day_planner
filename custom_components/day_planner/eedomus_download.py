"""Temporary, authenticated CSV/XLSX downloads for eedomus import associations.

The files are generated on demand while the options flow is open.  No copy of the
user's export or generated table is written to /config or served by /local.
"""

import csv
import re
import secrets
import time
from datetime import timedelta
from io import StringIO

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.auth import async_sign_path

from .eedomus_excel import xlsx_bytes

CSV_ENDPOINT = "/api/day_planner/eedomus_associations.csv"
XLSX_ENDPOINT = "/api/day_planner/eedomus_associations.xlsx"
_REPORTS_KEY = "day_planner_eedomus_csv_reports"
_VALID_SECONDS = 15 * 60
_MAX_PENDING_REPORTS = 40


def _csv_bytes(tsv: str) -> bytes:
    """Convert the already-sanitized, tab-separated preview into Excel CSV."""
    output = StringIO(newline="")
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    for line in tsv.splitlines():
        writer.writerow(line.split("\t"))
    # UTF-8 BOM helps French Windows Excel detect accented characters.
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def _csv_filename(host: str) -> str:
    """Build a safe, human-readable attachment name from the selected box."""
    safe_host = re.sub(r"[^a-zA-Z0-9_.-]", "_", host.strip())[:80]
    safe_host = safe_host.strip("._-") or "box"
    return f"day_planner_associations_eedomus_{safe_host}.csv"


def _prune_reports(reports: dict, now: float) -> None:
    """Keep only unexpired reports and limit memory usage."""
    for token, (expires, _body, _filename) in tuple(reports.items()):
        if expires <= now:
            del reports[token]
    while len(reports) >= _MAX_PENDING_REPORTS:
        del reports[next(iter(reports))]


def create_eedomus_csv_link(hass, tsv: str, host: str) -> str:
    """Return a short-lived signed link for the current options-flow table."""
    reports = hass.data.setdefault(_REPORTS_KEY, {})
    now = time.monotonic()
    _prune_reports(reports, now)
    token = secrets.token_urlsafe(32)
    reports[token] = (now + _VALID_SECONDS, _csv_bytes(tsv), _csv_filename(host))
    return async_sign_path(
        hass,
        f"{CSV_ENDPOINT}?token={token}",
        timedelta(seconds=_VALID_SECONDS),
    )


def create_eedomus_xlsx_link(hass, plan, host: str, agenda: dict | None = None) -> str:
    """Generate an in-memory seven-tab workbook and return a signed link."""
    reports = hass.data.setdefault(_REPORTS_KEY, {})
    now = time.monotonic()
    _prune_reports(reports, now)
    token = secrets.token_urlsafe(32)
    filename = _csv_filename(host).removesuffix(".csv") + ".xlsx"
    reports[token] = (now + _VALID_SECONDS, xlsx_bytes(plan, host, agenda), filename)
    return async_sign_path(
        hass,
        f"{XLSX_ENDPOINT}?token={token}",
        timedelta(seconds=_VALID_SECONDS),
    )


class EedomusAssociationsDownloadView(HomeAssistantView):
    """Send a pending eedomus association report as an Excel-compatible CSV."""

    url = CSV_ENDPOINT
    name = "api:day_planner:eedomus_associations"
    # Signed URLs are accepted by HA's normal auth middleware. Keep this True.
    requires_auth = True

    def __init__(self, hass) -> None:
        """Bind the view to one running Home Assistant instance."""
        self._hass = hass

    async def get(self, request: web.Request) -> web.Response:
        """Return a report only with its signed URL and unexpired token."""
        token = request.query.get("token", "")
        reports = self._hass.data.get(_REPORTS_KEY, {})
        report = reports.get(token)
        if report is None:
            raise web.HTTPNotFound()
        expires, body, filename = report
        if expires <= time.monotonic():
            del reports[token]
            raise web.HTTPNotFound()
        return web.Response(
            body=body,
            content_type="text/csv",
            charset="utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )


class EedomusAssociationsExcelView(EedomusAssociationsDownloadView):
    """Serve the complete Excel workbook, with all seven worksheets."""

    url = XLSX_ENDPOINT
    name = "api:day_planner:eedomus_associations_excel"

    async def get(self, request: web.Request) -> web.Response:
        """Preserve the signed-link token checks, with XLSX MIME type."""
        response = await super().get(request)
        response.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.charset = None
        return response
