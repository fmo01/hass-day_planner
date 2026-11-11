"""Tests for in-HA CSV downloads during the one-off eedomus import."""

import asyncio
import csv
from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from aiohttp import web

from custom_components.day_planner.eedomus_download import (
    CSV_ENDPOINT,
    EedomusAssociationsDownloadView,
    _csv_bytes,
    _csv_filename,
    _prune_reports,
    create_eedomus_csv_link,
)


def test_eedomus_download_csv_excel_columns_accents_and_quoting():
    source = (
        "Périphérique eedomus (ID)\tEntité Home Assistant\tStatut / motif\n"
        "Guirlande [746271]\tlight.guirlande\tPris en charge\n"
        "Volet; Séjour [795317]\tsensor.volet\tIgnoré : domaine sensor non pris en charge"
    )
    content = _csv_bytes(source)
    assert content.startswith(b"\xef\xbb\xbf")
    text = content.decode("utf-8-sig")
    assert "\r\n" in text
    reader = csv.reader(StringIO(text), delimiter=";")
    rows = list(reader)
    assert rows[0] == [
        "Périphérique eedomus (ID)",
        "Entité Home Assistant",
        "Statut / motif",
    ]
    assert rows[1][0] == "Guirlande [746271]"
    assert rows[2] == [
        "Volet; Séjour [795317]",
        "sensor.volet",
        "Ignoré : domaine sensor non pris en charge",
    ]


def test_eedomus_download_filename_sanitized():
    assert _csv_filename("192.20.55.30") == ("day_planner_associations_eedomus_192.20.55.30.csv")
    assert _csv_filename(' ../bad/"\r\n') == ("day_planner_associations_eedomus_bad.csv")
    assert _csv_filename(" . ") == "day_planner_associations_eedomus_box.csv"
    assert len(_csv_filename("A" * 200)) <= 120


def test_eedomus_download_link_is_signed_and_not_written_to_disk():
    hass = MagicMock()
    hass.data = {}
    with patch(
        "custom_components.day_planner.eedomus_download.async_sign_path",
        side_effect=lambda _hass, path, _expiry: path + "&authSig=SIGNED",
    ) as sign:
        url = create_eedomus_csv_link(hass, "eedomus\thome assistant\tstatut\n", "192.20.55.30")
    parsed = urlparse(url)
    assert parsed.path == CSV_ENDPOINT
    assert parse_qs(parsed.query)["authSig"] == ["SIGNED"]
    token = parse_qs(parsed.query)["token"][0]
    assert len(token) >= 32
    sign.assert_called_once()
    assert sign.call_args.args[2].total_seconds() == 900
    record = hass.data["day_planner_eedomus_csv_reports"][token]
    assert record[1].startswith(b"\xef\xbb\xbf")
    assert record[2].endswith("192.20.55.30.csv")


def test_eedomus_download_authenticated_view_response_and_not_found():
    hass = MagicMock()
    hass.data = {}
    with patch(
        "custom_components.day_planner.eedomus_download.async_sign_path",
        side_effect=lambda _hass, path, _expiry: path + "&authSig=test",
    ):
        url = create_eedomus_csv_link(hass, "Volet\tsensor.volet\tIgnoré", "192.20.55.30")
    token = parse_qs(urlparse(url).query)["token"][0]
    view = EedomusAssociationsDownloadView(hass)
    assert view.requires_auth is True
    assert view.url == CSV_ENDPOINT

    async def run():
        response = await view.get(SimpleNamespace(query={"token": token}))
        assert response.status == 200
        assert "attachment; filename=" in response.headers["Content-Disposition"]
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "sensor.volet" in response.body.decode("utf-8-sig")
        with pytest.raises(web.HTTPNotFound):
            await view.get(SimpleNamespace(query={"token": "bad"}))
        with pytest.raises(web.HTTPNotFound):
            await view.get(SimpleNamespace(query={}))

    asyncio.run(run())


def test_eedomus_download_rejects_expired_token():
    hass = MagicMock()
    hass.data = {"day_planner_eedomus_csv_reports": {"tok": (5, b"data", "test.csv")}}
    view = EedomusAssociationsDownloadView(hass)

    async def run():
        with patch(
            "custom_components.day_planner.eedomus_download.time.monotonic",
            return_value=6,
        ):
            with pytest.raises(web.HTTPNotFound):
                await view.get(SimpleNamespace(query={"token": "tok"}))
        assert "tok" not in hass.data["day_planner_eedomus_csv_reports"]

    asyncio.run(run())


def test_eedomus_download_expired_and_bounded_report_cache():
    reports = {"expired": (2, b"old", "old.csv")}
    for i in range(40):
        reports[str(i)] = (1000, b"new", "new.csv")
    _prune_reports(reports, 10)
    assert "expired" not in reports
    assert len(reports) == 39
    assert "0" not in reports


def test_eedomus_excel_link_is_signed_and_has_excel_mime_type():
    from types import SimpleNamespace
    from unittest.mock import MagicMock, patch

    from custom_components.day_planner.eedomus_download import (
        XLSX_ENDPOINT,
        EedomusAssociationsExcelView,
        create_eedomus_xlsx_link,
    )

    plan = SimpleNamespace(
        mapped_entities=("Guirlande [1] → light.guirlande",),
        unsupported_associations=(),
        day_types=1,
        moments=1,
        scheduled=1,
        actions=1,
        moments_without_actions=0,
        conditional_rules_not_imported=0,
        unresolved_embedded_parameters=0,
        had_previous_import=False,
    )
    hass = MagicMock()
    hass.data = {}
    with patch(
        "custom_components.day_planner.eedomus_download.async_sign_path",
        side_effect=lambda _hass, path, _expiry: path + "&authSig=test",
    ):
        agenda = {"regles_conditionnelles_liees_agenda": [{"id": "777", "nom": "Non reprise", "active": True}]}
        url = create_eedomus_xlsx_link(hass, plan, "192.20.55.30", agenda)
    parsed = urlparse(url)
    assert parsed.path == XLSX_ENDPOINT
    token = parse_qs(parsed.query)["token"][0]
    assert hass.data["day_planner_eedomus_csv_reports"][token][1].startswith(b"PK")
    from io import BytesIO
    from zipfile import ZipFile

    with ZipFile(BytesIO(hass.data["day_planner_eedomus_csv_reports"][token][1])) as book:
        assert b"Non reprise" in book.read("xl/worksheets/sheet5.xml")
        assert "xl/worksheets/sheet7.xml" in book.namelist()
    assert hass.data["day_planner_eedomus_csv_reports"][token][2].endswith(".xlsx")
    view = EedomusAssociationsExcelView(hass)

    async def run():
        response = await view.get(SimpleNamespace(query={"token": token}))
        assert response.status == 200
        assert response.content_type == ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        assert response.charset is None
        assert response.headers["Content-Disposition"].endswith('.xlsx"')
        with pytest.raises(web.HTTPNotFound):
            await view.get(SimpleNamespace(query={"token": "bad"}))

    asyncio.run(run())
