"""Options flow for Day Planner."""

import hashlib
import html
import json
import logging
from datetime import date, time

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.helpers import selector

from .const import (
    CONF_DELETE_DATA_ON_REMOVE,
    CONF_MAX_CYCLES,
    CONF_SHOW_SIDEBAR_PANEL,
    DEFAULT_DELETE_DATA_ON_REMOVE,
    DEFAULT_MAX_CYCLES,
    DEFAULT_SHOW_SIDEBAR_PANEL,
    MAX_MAX_CYCLES,
    MIN_MAX_CYCLES,
    PANEL_URL_PATH,
)
from .domain.action import Action
from .domain.calendar_exception import CalendarException
from .domain.cycle import Cycle
from .domain.day_type import DayType
from .domain.moment import Moment
from .domain.scheduled_moment import ScheduledMoment
from .domain.time_definition import TimeDefinition
from .domain.week_schedule import WeekSchedule
from .eedomus_download import create_eedomus_csv_link, create_eedomus_xlsx_link
from .eedomus_import import (
    EedomusImportError,
    create_import_plan,
    get_eedomus_entity_map,
    prepare_import,
)
from .planner.errors import ValidationError

_LOGGER = logging.getLogger(__name__)


class DayPlannerOptionsFlow(
    config_entries.OptionsFlow,
):
    """Handle Day Planner options."""

    def __init__(self) -> None:
        """Initialize options flow."""

        self._selected_moment_id: str | None = None
        self._selected_day_type_id: str | None = None
        self._selected_remove_day_type_id: str | None = None
        self._selected_scheduled_day_type_id: str | None = None
        self._selected_scheduled_moment_id: str | None = None
        self._selected_remove_scheduled_moment_id: str | None = None
        self._selected_week_schedule_id: str | None = None
        self._selected_remove_week_schedule_id: str | None = None
        self._selected_cycle_id: str | None = None
        self._selected_remove_cycle_id: str | None = None
        self._selected_calendar_exception_id: str | None = None
        self._selected_remove_calendar_exception_id: str | None = None
        self._selected_action_moment_id: str | None = None
        self._selected_action_id: str | None = None
        self._selected_remove_action_id: str | None = None
        self._eedomus_import_source: str | None = None
        self._eedomus_import_agenda: dict | None = None
        self._eedomus_configuration_digest: str | None = None

    async def async_step_init(
        self,
        user_input=None,
    ):
        """Show Day Planner options menu."""

        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "management",
                "moments",
                "day_types",
                "week_schedules",
                "cycles",
                "calendar_exceptions",
                "settings",
                "import_eedomus",
            ],
        )

    @staticmethod
    def _eedomus_digest(configuration):
        """Detect concurrent edits during the confirmation step."""
        serialized = json.dumps(configuration.to_dict(), sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    async def _eedomus_actor(self):
        """Use the HA display name for audit where available."""
        user_id = self.context.get("user_id")
        if not user_id:
            return "system"
        user = await self.hass.auth.async_get_user(user_id)
        return (user.name or user.id) if user is not None else user_id

    async def _eedomus_read_upload(self, uploaded_file_id, source_entry_id):
        """Consume a browser-uploaded JSON in an executor; HA deletes the upload."""

        def read_file():
            with process_uploaded_file(self.hass, uploaded_file_id) as path:
                if path.suffix.lower() != ".json":
                    raise EedomusImportError("Le fichier doit être au format JSON")
                if not path.is_file() or path.stat().st_size > 20 * 1024 * 1024:
                    raise EedomusImportError("JSON introuvable ou supérieur à 20 Mo")
                # The uploaded raw export stays temporary and is deleted by HA
                # on leaving the process_uploaded_file context manager.
                return prepare_import(self.hass, source_entry_id, path)

        return await self.hass.async_add_executor_job(read_file)

    @staticmethod
    def _eedomus_entry_active(entry):
        """Only enabled, successfully loaded eedomus integrations are importable."""
        return (
            entry.domain == "eedomus"
            and entry.disabled_by is None
            and entry.state is config_entries.ConfigEntryState.LOADED
        )

    async def _eedomus_plan(self, source_entry_id, agenda):
        """Validate imported data and HA entity mapping, without saving."""
        source = self.hass.config_entries.async_get_entry(source_entry_id)
        if source is None or not self._eedomus_entry_active(source):
            raise EedomusImportError(
                "La box eedomus sélectionnée est désactivée ou non chargée dans Home Assistant"
            )
        runtime = self.config_entry.runtime_data
        # Use api_host for all imported names AND Day Planner IDs. HA's own
        # entity unique_ids still require source_entry_id for registry lookup.
        host = source.data.get("api_host")
        if not isinstance(host, str) or not host.strip():
            raise EedomusImportError(
                "Adresse de la box eedomus absente (api_host) : reprise impossible"
            )
        week_name = f"Eedomus ({host.strip()})"
        # Without the config entry ID in imported object IDs, two active HA
        # entries pointing at the same host would have identical IDs.
        duplicates = [
            entry
            for entry in self.hass.config_entries.async_entries("eedomus")
            if entry.entry_id != source_entry_id
            and self._eedomus_entry_active(entry)
            and isinstance(entry.data.get("api_host"), str)
            and entry.data["api_host"].strip() == host.strip()
        ]
        if duplicates:
            raise EedomusImportError(
                f"Plusieurs intégrations eedomus actives utilisent {host} : "
                "impossible de distinguer leurs objets Day Planner"
            )
        return create_import_plan(
            agenda,
            runtime.engine.configuration,
            source_entry_id,
            get_eedomus_entity_map(self.hass, source_entry_id),
            replace_existing=True,
            actor=await self._eedomus_actor(),
            max_cycles=runtime.engine.max_cycles,
            week_name=week_name,
        )

    async def async_step_import_eedomus(self, user_input=None):
        """One-shot import: choose HA eedomus config entry and browser JSON."""
        available = self.hass.config_entries.async_entries("eedomus")
        if not available:
            return self.async_abort(reason="eedomus_not_configured")
        entries = [entry for entry in available if self._eedomus_entry_active(entry)]
        if not entries:
            return self.async_abort(reason="eedomus_not_active")
        # A single existing config entry identifies the source unambiguously;
        # ask the user to choose only when multiple eedomus boxes exist.
        fields = {}
        if len(entries) > 1:
            fields[vol.Required("source_entry_id")] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=e.entry_id, label=f"{e.title} ({e.entry_id})"
                        )
                        for e in entries
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        fields[vol.Required("json_upload")] = selector.FileSelector(
            selector.FileSelectorConfig(accept=".json,application/json")
        )
        schema = vol.Schema(fields)
        errors = {}
        details = ""
        if user_input is not None:
            try:
                source_id = (
                    entries[0].entry_id
                    if len(entries) == 1
                    else user_input["source_entry_id"]
                )
                if not any(entry.entry_id == source_id for entry in entries):
                    raise EedomusImportError("Box eedomus sélectionnée introuvable")
                source = self.hass.config_entries.async_get_entry(source_id)
                if source is None or not self._eedomus_entry_active(source):
                    raise EedomusImportError(
                        "Box eedomus sélectionnée désactivée ou non chargée dans Home Assistant"
                    )
                agenda = await self._eedomus_read_upload(
                    user_input["json_upload"], source_id
                )
                await self._eedomus_plan(source_id, agenda)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                _LOGGER.warning("eedomus import preflight rejected: %s", exc)
                errors["base"] = "eedomus_import_invalid"
                details = (
                    f"ÉCHEC DU CONTRÔLE — {exc}. "
                    "Aucune donnée n'a été importée dans Day Planner."
                )
            else:
                self._eedomus_import_source = source_id
                self._eedomus_import_agenda = agenda
                self._eedomus_configuration_digest = self._eedomus_digest(
                    self.config_entry.runtime_data.engine.configuration
                )
                return await self.async_step_import_eedomus_confirm()
        return self.async_show_form(
            step_id="import_eedomus",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "details": details,
                "eedomus_export_url": "https://secure.eedomus.com/import_export",
                "box_count": str(len(entries)),
                "selected_box": (
                    f"{entries[0].title} ({entries[0].entry_id})"
                    if len(entries) == 1
                    else ""
                ),
            },
        )

    @staticmethod
    def _eedomus_mappings_table(mapped_entities, unsupported_associations=()):
        """Show supported and skipped associations together in the same table.

        Every eedomus command with a registered but unsupported HA target
        remains visible, including sensor and binary_sensor domains. No
        unsupported association becomes a Day Planner action.
        """

        def escape_cell(value):
            """Avoid broken Markdown table cells from registry device names."""
            return (
                str(value)
                .replace("\\", "\\\\")
                .replace("|", "\\|")
                .replace("`", "\\`")
                .replace("\r", " ")
                .replace("\n", " ")
            )

        rows = []
        for association in mapped_entities:
            eedomus, separator, entity_id = association.rpartition(" → ")
            if not separator:
                eedomus, entity_id = association, "—"
            rows.append(
                f"| {escape_cell(eedomus)} | `{escape_cell(entity_id)}` | Pris en charge |"
            )

        for peripheral, entity_id, reason in unsupported_associations:
            rows.append(
                f"| {escape_cell(peripheral)} | `{escape_cell(entity_id)}` | "
                f"Ignoré : {escape_cell(reason)} |"
            )
        return "\n".join(rows) if rows else "| — | — | Aucune association |"

    @staticmethod
    def _eedomus_unsupported_table(associations):
        """Render skipped, incompatible eedomus-to-HA associations in Markdown."""
        if not associations:
            return "| — | — | — |"

        def safe(value):
            return (
                str(value)
                .replace("\\", "\\\\")
                .replace("|", "\\|")
                .replace("`", "\\`")
                .replace("\r", " ")
                .replace("\n", " ")
            )

        return "\n".join(
            f"| {safe(peripheral)} | `{safe(entity_id)}` | {safe(reason)} |"
            for peripheral, entity_id, reason in associations
        )

    @staticmethod
    def _eedomus_copy_table(mapped_entities, unsupported_associations):
        """Prepare Excel-ready, tab-separated associations for clipboard copying."""

        def safe_cell(value):
            """Prevent row breaks and spreadsheet formula evaluation."""
            cell = " ".join(str(value).split())
            if cell.lstrip().startswith(("=", "+", "-", "@")):
                return "'" + cell
            return cell

        rows = [
            (
                "Périphérique eedomus (ID)",
                "Entité Home Assistant",
                "Statut / motif",
            )
        ]
        for association in mapped_entities:
            peripheral, separator, entity_id = association.rpartition(" → ")
            if not separator:
                peripheral, entity_id = association, "—"
            rows.append((peripheral, entity_id, "Pris en charge"))

        for peripheral, entity_id, reason in unsupported_associations:
            rows.append((peripheral, entity_id, f"Ignoré : {reason}"))

        return "\n".join("\t".join(safe_cell(cell) for cell in row) for row in rows)

    @staticmethod
    def _eedomus_csv_download_url(hass, tsv, host):
        """Make a short-lived download link; do not persist the associations."""
        return create_eedomus_csv_link(hass, tsv, host)

    @staticmethod
    def _eedomus_xlsx_download_url(hass, plan, host, agenda=None):
        """Generate the seven-sheet Excel export from the validated plan."""
        return create_eedomus_xlsx_link(hass, plan, host, agenda)

    async def async_step_import_eedomus_confirm(self, user_input=None):
        """Explicit confirmation, mandatory when replacing prior import."""
        if self._eedomus_import_source is None or self._eedomus_import_agenda is None:
            return await self.async_step_import_eedomus()
        errors = {}
        try:
            plan = await self._eedomus_plan(
                self._eedomus_import_source, self._eedomus_import_agenda
            )
            runtime = self.config_entry.runtime_data
            if (
                self._eedomus_digest(runtime.engine.configuration)
                != self._eedomus_configuration_digest
            ):
                raise EedomusImportError(
                    "Configuration Day Planner modifiée pendant la confirmation"
                )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            _LOGGER.warning("eedomus confirmation rejected: %s", exc)
            return self.async_show_form(
                step_id="import_eedomus_confirm",
                data_schema=vol.Schema({}),
                errors={"base": "eedomus_import_changed"},
            )

        # HA's config-flow frontend turns selector read_only=True into a
        # disabled field (no selection/copy, forbidden cursor).  Keep this
        # optional textarea enabled for selection/clipboard access instead.
        # Its submitted value is NEVER read or used to build the import plan.
        copy_table = self._eedomus_copy_table(
            plan.mapped_entities, plan.unsupported_associations
        )
        schema = vol.Schema(
            {
                vol.Optional(
                    "associations_excel", default=copy_table
                ): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
                vol.Required("confirm", default=False): bool,
                vol.Optional("replace_existing", default=False): bool,
            }
        )
        if user_input is not None:
            if not user_input.get("confirm"):
                errors["base"] = "eedomus_confirm_required"
            elif plan.had_previous_import and not user_input.get("replace_existing"):
                errors["base"] = "eedomus_replace_required"
            else:
                previous = runtime.engine.configuration
                try:
                    runtime.engine.replace_configuration(plan.configuration)
                    await runtime.async_configuration_updated()
                except Exception:
                    # Restore the prior runtime and best-effort persist/reschedule.
                    _LOGGER.exception("eedomus import failed during persistence")
                    runtime.engine.replace_configuration(previous)
                    try:
                        await runtime.async_configuration_updated()
                    except Exception:
                        _LOGGER.exception("eedomus rollback failed")
                    errors["base"] = "eedomus_import_failed"
                else:
                    return self.async_create_entry(
                        title="",
                        data=self.config_entry.options,
                    )
        # Only publish a fresh link if the confirmation is actually displayed.
        source = self.hass.config_entries.async_get_entry(self._eedomus_import_source)
        host = source.data.get("api_host", "box") if source else "box"
        if not isinstance(host, str):
            host = "box"
        download_url = self._eedomus_xlsx_download_url(
            self.hass, plan, host, self._eedomus_import_agenda
        )
        # Keep markup out of translation strings: ICU rejects literal <a> tags.
        # The frontend Markdown sanitizer permits target=_blank on anchors,
        # preventing the HA SPA router from intercepting a normal click.
        download_link = (
            f'<a href="{html.escape(download_url, quote=True)}" '
            f'target="_blank">📥 Télécharger le classeur Excel (.xlsx)</a>'
        )
        summary = (
            f"{plan.day_types} journées, {plan.moments} moments, "
            f"{plan.scheduled} horaires, {plan.actions} actions. "
            f"{plan.moments_without_actions} moment(s) sans action compatible."
        )
        limitations = (
            f"{plan.conditional_rules_not_imported} règles conditionnelles actives "
            f"et {plan.unresolved_embedded_parameters} paramètres internes non repris."
        )
        return self.async_show_form(
            step_id="import_eedomus_confirm",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "summary": summary,
                "limitations": limitations,
                "download_url": download_url,
                "download_link": download_link,
                "mappings": self._eedomus_mappings_table(
                    plan.mapped_entities, plan.unsupported_associations
                ),
                "unsupported": self._eedomus_unsupported_table(
                    plan.unsupported_associations
                ),
                "unsupported_count": str(len(plan.unsupported_associations)),
                "replacement": ("Oui" if plan.had_previous_import else "Non"),
            },
        )

    async def async_step_management(self, user_input=None):
        """Offer a link to the existing graphical management interface."""
        if user_input is not None:
            return await self.async_step_init()

        return self.async_show_form(
            step_id="management",
            data_schema=vol.Schema({}),
            description_placeholders={"url": f"/{PANEL_URL_PATH}"},
        )

    async def async_step_calendar_exceptions(
        self,
        user_input=None,
    ):
        """Manage calendar exceptions."""

        return self.async_show_menu(
            step_id="calendar_exceptions",
            menu_options=[
                "add_calendar_exception",
                "edit_calendar_exception",
                "remove_calendar_exception",
            ],
        )

    async def async_step_settings(
        self,
        user_input=None,
    ):
        """Manage Day Planner settings."""

        current_cycle_count = len(
            self.config_entry.runtime_data.engine.configuration.cycles
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SHOW_SIDEBAR_PANEL,
                    default=self.config_entry.options.get(
                        CONF_SHOW_SIDEBAR_PANEL,
                        DEFAULT_SHOW_SIDEBAR_PANEL,
                    ),
                ): bool,
                vol.Optional(
                    CONF_DELETE_DATA_ON_REMOVE,
                    default=self.config_entry.options.get(
                        CONF_DELETE_DATA_ON_REMOVE,
                        DEFAULT_DELETE_DATA_ON_REMOVE,
                    ),
                ): bool,
                vol.Optional(
                    CONF_MAX_CYCLES,
                    default=self.config_entry.options.get(
                        CONF_MAX_CYCLES,
                        DEFAULT_MAX_CYCLES,
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_MAX_CYCLES,
                        max=MAX_MAX_CYCLES,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        if user_input is not None:
            user_input = dict(user_input)

            max_cycles = int(
                user_input.get(
                    CONF_MAX_CYCLES,
                    self.config_entry.options.get(
                        CONF_MAX_CYCLES,
                        DEFAULT_MAX_CYCLES,
                    ),
                )
            )

            if max_cycles < current_cycle_count:
                return self.async_show_form(
                    step_id="settings",
                    data_schema=schema,
                    errors={
                        "base": "max_cycles_too_small",
                    },
                    description_placeholders={
                        "value": str(max_cycles),
                        "minimum": str(current_cycle_count),
                    },
                )

            user_input[CONF_MAX_CYCLES] = max_cycles

            return self.async_create_entry(
                title="",
                data={**self.config_entry.options, **user_input},
            )

        return self.async_show_form(
            step_id="settings",
            data_schema=schema,
        )

    async def async_step_moments(
        self,
        user_input=None,
    ):
        """Manage moments."""

        return self.async_show_menu(
            step_id="moments",
            menu_options=[
                "add_moment",
                "edit_moment",
                "remove_moment",
                "moment_actions",
            ],
        )

    async def async_step_add_moment(
        self,
        user_input=None,
    ):
        """Add a moment."""

        if user_input is not None:
            entry = self.config_entry
            runtime = entry.runtime_data

            moment = Moment(
                id=user_input["id"],
                name=user_input["name"],
                icon=user_input.get("icon"),
                actions=(),
            )

            runtime.engine.add_moment(
                moment,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("name"): str,
                vol.Optional("icon"): selector.IconSelector(),
            }
        )

        return self.async_show_form(
            step_id="add_moment",
            data_schema=schema,
        )

    async def async_step_edit_moment(
        self,
        user_input=None,
    ):
        """Edit a moment."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_moment_id = user_input["id"]

            return await self.async_step_edit_moment_details()

        moments = runtime.engine.configuration.moments

        moment_options = [
            selector.SelectOptionDict(
                value=moment.id,
                label=moment.name,
            )
            for moment in moments
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=moment_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_moment",
            data_schema=schema,
        )

    async def async_step_edit_moment_details(
        self,
        user_input=None,
    ):
        """Edit the selected moment."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_moment_id)

        if user_input is not None:
            updated_moment = Moment(
                id=moment.id,
                name=user_input["name"],
                icon=user_input.get("icon"),
                actions=moment.actions,
            )

            runtime.engine.update_moment(
                updated_moment,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "name",
                    default=moment.name,
                ): str,
                vol.Optional(
                    "icon",
                    default=moment.icon,
                ): selector.IconSelector(),
            }
        )

        return self.async_show_form(
            step_id="edit_moment_details",
            data_schema=schema,
        )

    async def async_step_remove_moment(
        self,
        user_input=None,
    ):
        """Select a moment to remove."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_remove_moment_id = user_input["id"]

            return await self.async_step_remove_moment_confirm()

        moments = runtime.engine.configuration.moments

        moment_options = [
            selector.SelectOptionDict(
                value=moment.id,
                label=moment.name,
            )
            for moment in moments
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=moment_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_moment",
            data_schema=schema,
        )

    async def async_step_remove_moment_confirm(
        self,
        user_input=None,
    ):
        """Confirm removal of a moment."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_remove_moment_id)

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_moment_confirm",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                "confirm",
                                default=False,
                            ): bool,
                        }
                    ),
                    description_placeholders={
                        "name": moment.name,
                    },
                )

            runtime.engine.remove_moment(moment.id)

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="remove_moment_confirm",
            data_schema=schema,
            description_placeholders={
                "name": moment.name,
            },
        )

    async def async_step_day_types(
        self,
        user_input=None,
    ):
        """Manage day types."""

        return self.async_show_menu(
            step_id="day_types",
            menu_options=[
                "add_day_type",
                "edit_day_type",
                "remove_day_type",
                "scheduled_moments",
            ],
        )

    async def async_step_week_schedules(
        self,
        user_input=None,
    ):
        """Manage week schedules."""

        return self.async_show_menu(
            step_id="week_schedules",
            menu_options=[
                "add_week_schedule",
                "edit_week_schedule",
                "remove_week_schedule",
            ],
        )

    async def async_step_cycles(
        self,
        user_input=None,
    ):
        """Manage cycles."""

        runtime = self.config_entry.runtime_data

        cycle_count = len(runtime.engine.configuration.cycles)

        menu_options = []

        if cycle_count < runtime.engine.max_cycles:
            menu_options.append("add_cycle")

        if cycle_count > 0:
            menu_options.extend(
                [
                    "edit_cycle",
                    "remove_cycle",
                ]
            )

        return self.async_show_menu(
            step_id="cycles",
            menu_options=menu_options,
        )

    async def async_step_add_day_type(
        self,
        user_input=None,
    ):
        """Add a day type."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            day_type = DayType(
                id=user_input["id"],
                name=user_input["name"],
                scheduled_moments=(),
            )

            runtime.engine.add_day_type(
                day_type,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("name"): str,
            }
        )

        return self.async_show_form(
            step_id="add_day_type",
            data_schema=schema,
        )

    async def async_step_edit_day_type(
        self,
        user_input=None,
    ):
        """Select a day type to edit."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_day_type_id = user_input["id"]

            return await self.async_step_edit_day_type_details()

        day_types = runtime.engine.configuration.day_types

        options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in day_types
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_day_type",
            data_schema=schema,
        )

    async def async_step_edit_day_type_details(
        self,
        user_input=None,
    ):
        """Edit selected day type."""

        runtime = self.config_entry.runtime_data

        day_type = runtime.engine.get_day_type(self._selected_day_type_id)

        if user_input is not None:
            updated_day_type = DayType(
                id=day_type.id,
                name=user_input["name"],
                scheduled_moments=day_type.scheduled_moments,
            )

            runtime.engine.update_day_type(
                updated_day_type,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "name",
                    default=day_type.name,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="edit_day_type_details",
            data_schema=schema,
        )

    async def async_step_remove_day_type(
        self,
        user_input=None,
    ):
        """Select a day type to remove."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_remove_day_type_id = user_input["id"]

            return await self.async_step_remove_day_type_confirm()

        day_types = runtime.engine.configuration.day_types

        options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in day_types
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_day_type",
            data_schema=schema,
        )

    async def async_step_remove_day_type_confirm(
        self,
        user_input=None,
    ):
        """Confirm day type removal."""

        runtime = self.config_entry.runtime_data

        day_type = runtime.engine.get_day_type(self._selected_remove_day_type_id)

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_day_type_confirm",
                    data_schema=schema,
                    description_placeholders={
                        "name": day_type.name,
                    },
                )

            try:
                runtime.engine.remove_day_type(day_type.id)
            except ValidationError:
                return self.async_show_form(
                    step_id="remove_day_type_confirm",
                    data_schema=schema,
                    errors={
                        "base": "day_type_in_use",
                    },
                    description_placeholders={
                        "name": day_type.name,
                    },
                )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="remove_day_type_confirm",
            data_schema=schema,
            description_placeholders={
                "name": day_type.name,
            },
        )

    async def async_step_scheduled_moments(
        self,
        user_input=None,
    ):
        """Select a day type for scheduled moments."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_scheduled_day_type_id = user_input["day_type_id"]

            return await self.async_step_scheduled_moments_menu()

        day_types = runtime.engine.configuration.day_types

        options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in day_types
        ]

        schema = vol.Schema(
            {
                vol.Required("day_type_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="scheduled_moments",
            data_schema=schema,
        )

    async def async_step_scheduled_moments_menu(
        self,
        user_input=None,
    ):
        """Manage scheduled moments."""

        return self.async_show_menu(
            step_id="scheduled_moments_menu",
            menu_options=[
                "add_scheduled_moment",
                "edit_scheduled_moment",
                "remove_scheduled_moment",
            ],
        )

    async def async_step_add_scheduled_moment(
        self,
        user_input=None,
    ):
        """Add a scheduled moment."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            scheduled_moment = ScheduledMoment(
                moment_id=user_input["moment_id"],
                time_definition=TimeDefinition(
                    fixed_time=time.fromisoformat(user_input["time"]),
                ),
            )

            runtime.engine.add_scheduled_moment(
                self._selected_scheduled_day_type_id,
                scheduled_moment,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        moments = runtime.engine.configuration.moments

        moment_options = [
            selector.SelectOptionDict(
                value=moment.id,
                label=moment.name,
            )
            for moment in moments
        ]

        schema = vol.Schema(
            {
                vol.Required("moment_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=moment_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required("time"): selector.TimeSelector(),
            }
        )

        return self.async_show_form(
            step_id="add_scheduled_moment",
            data_schema=schema,
        )

    async def async_step_edit_scheduled_moment(
        self,
        user_input=None,
    ):
        """Select a scheduled moment to edit."""

        runtime = self.config_entry.runtime_data

        day_type = runtime.engine.get_day_type(self._selected_scheduled_day_type_id)

        if user_input is not None:
            self._selected_scheduled_moment_id = user_input["moment_id"]

            return await self.async_step_edit_scheduled_moment_details()

        moment_names = {
            moment.id: moment.name for moment in runtime.engine.configuration.moments
        }

        options = [
            selector.SelectOptionDict(
                value=scheduled.moment_id,
                label=moment_names.get(
                    scheduled.moment_id,
                    scheduled.moment_id,
                ),
            )
            for scheduled in day_type.scheduled_moments
        ]

        schema = vol.Schema(
            {
                vol.Required("moment_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_scheduled_moment",
            data_schema=schema,
        )

    async def async_step_edit_scheduled_moment_details(
        self,
        user_input=None,
    ):
        """Edit a scheduled moment."""

        runtime = self.config_entry.runtime_data

        day_type = runtime.engine.get_day_type(self._selected_scheduled_day_type_id)

        scheduled_moment = next(
            item
            for item in day_type.scheduled_moments
            if item.moment_id == self._selected_scheduled_moment_id
        )

        moment = runtime.engine.get_moment(scheduled_moment.moment_id)

        if user_input is not None:
            updated = ScheduledMoment(
                moment_id=scheduled_moment.moment_id,
                time_definition=TimeDefinition(
                    fixed_time=time.fromisoformat(user_input["time"]),
                ),
            )

            runtime.engine.update_scheduled_moment(
                self._selected_scheduled_day_type_id,
                updated,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "time",
                    default=(scheduled_moment.time_definition.fixed_time.isoformat()),
                ): selector.TimeSelector(),
            }
        )

        return self.async_show_form(
            step_id="edit_scheduled_moment_details",
            data_schema=schema,
            description_placeholders={
                "name": moment.name,
            },
        )

    async def async_step_remove_scheduled_moment(
        self,
        user_input=None,
    ):
        """Select a scheduled moment to remove."""

        runtime = self.config_entry.runtime_data

        day_type = runtime.engine.get_day_type(self._selected_scheduled_day_type_id)

        if user_input is not None:
            self._selected_remove_scheduled_moment_id = user_input["moment_id"]

            return await self.async_step_remove_scheduled_moment_confirm()

        moment_names = {
            moment.id: moment.name for moment in runtime.engine.configuration.moments
        }

        options = [
            selector.SelectOptionDict(
                value=scheduled.moment_id,
                label=moment_names.get(
                    scheduled.moment_id,
                    scheduled.moment_id,
                ),
            )
            for scheduled in day_type.scheduled_moments
        ]

        schema = vol.Schema(
            {
                vol.Required("moment_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_scheduled_moment",
            data_schema=schema,
        )

    async def async_step_remove_scheduled_moment_confirm(
        self,
        user_input=None,
    ):
        """Confirm scheduled moment removal."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_remove_scheduled_moment_id)

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_scheduled_moment_confirm",
                    data_schema=schema,
                    description_placeholders={
                        "name": moment.name,
                    },
                )

            runtime.engine.remove_scheduled_moment(
                self._selected_scheduled_day_type_id,
                self._selected_remove_scheduled_moment_id,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="remove_scheduled_moment_confirm",
            data_schema=schema,
            description_placeholders={
                "name": moment.name,
            },
        )

    async def async_step_add_week_schedule(
        self,
        user_input=None,
    ):
        """Add a week schedule."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            week_schedule = WeekSchedule(
                id=user_input["id"],
                name=user_input["name"],
                monday=user_input["monday"],
                tuesday=user_input["tuesday"],
                wednesday=user_input["wednesday"],
                thursday=user_input["thursday"],
                friday=user_input["friday"],
                saturday=user_input["saturday"],
                sunday=user_input["sunday"],
            )

            runtime.engine.add_week_schedule(
                week_schedule,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        day_type_options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in runtime.engine.configuration.day_types
        ]

        day_selector = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=day_type_options,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("name"): str,
                vol.Required("monday"): day_selector,
                vol.Required("tuesday"): day_selector,
                vol.Required("wednesday"): day_selector,
                vol.Required("thursday"): day_selector,
                vol.Required("friday"): day_selector,
                vol.Required("saturday"): day_selector,
                vol.Required("sunday"): day_selector,
            }
        )

        return self.async_show_form(
            step_id="add_week_schedule",
            data_schema=schema,
        )

    async def async_step_edit_week_schedule(
        self,
        user_input=None,
    ):
        """Select a week schedule to edit."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_week_schedule_id = user_input["id"]

            return await self.async_step_edit_week_schedule_details()

        options = [
            selector.SelectOptionDict(
                value=week_schedule.id,
                label=week_schedule.name,
            )
            for week_schedule in runtime.engine.configuration.week_schedules
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_week_schedule",
            data_schema=schema,
        )

    async def async_step_edit_week_schedule_details(
        self,
        user_input=None,
    ):
        """Edit selected week schedule."""

        runtime = self.config_entry.runtime_data

        week_schedule = runtime.engine.get_week_schedule(
            self._selected_week_schedule_id
        )

        if user_input is not None:
            updated = WeekSchedule(
                id=week_schedule.id,
                name=user_input["name"],
                monday=user_input["monday"],
                tuesday=user_input["tuesday"],
                wednesday=user_input["wednesday"],
                thursday=user_input["thursday"],
                friday=user_input["friday"],
                saturday=user_input["saturday"],
                sunday=user_input["sunday"],
            )

            runtime.engine.update_week_schedule(
                updated,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        day_type_options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in runtime.engine.configuration.day_types
        ]

        def day_selector():
            return selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=day_type_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "name",
                    default=week_schedule.name,
                ): str,
                vol.Required(
                    "monday",
                    default=week_schedule.monday,
                ): day_selector(),
                vol.Required(
                    "tuesday",
                    default=week_schedule.tuesday,
                ): day_selector(),
                vol.Required(
                    "wednesday",
                    default=week_schedule.wednesday,
                ): day_selector(),
                vol.Required(
                    "thursday",
                    default=week_schedule.thursday,
                ): day_selector(),
                vol.Required(
                    "friday",
                    default=week_schedule.friday,
                ): day_selector(),
                vol.Required(
                    "saturday",
                    default=week_schedule.saturday,
                ): day_selector(),
                vol.Required(
                    "sunday",
                    default=week_schedule.sunday,
                ): day_selector(),
            }
        )

        return self.async_show_form(
            step_id="edit_week_schedule_details",
            data_schema=schema,
        )

    async def async_step_remove_week_schedule(
        self,
        user_input=None,
    ):
        """Select a week schedule to remove."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_remove_week_schedule_id = user_input["id"]

            return await self.async_step_remove_week_schedule_confirm()

        options = [
            selector.SelectOptionDict(
                value=week_schedule.id,
                label=week_schedule.name,
            )
            for week_schedule in runtime.engine.configuration.week_schedules
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_week_schedule",
            data_schema=schema,
        )

    async def async_step_remove_week_schedule_confirm(
        self,
        user_input=None,
    ):
        """Confirm week schedule removal."""

        runtime = self.config_entry.runtime_data

        week_schedule = runtime.engine.get_week_schedule(
            self._selected_remove_week_schedule_id
        )

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_week_schedule_confirm",
                    data_schema=schema,
                    description_placeholders={
                        "name": week_schedule.name,
                    },
                )

            try:
                runtime.engine.remove_week_schedule(week_schedule.id)
            except ValidationError:
                return self.async_show_form(
                    step_id="remove_week_schedule_confirm",
                    data_schema=schema,
                    errors={
                        "base": "week_schedule_in_use",
                    },
                    description_placeholders={
                        "name": week_schedule.name,
                    },
                )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="remove_week_schedule_confirm",
            data_schema=schema,
            description_placeholders={
                "name": week_schedule.name,
            },
        )

    async def async_step_add_cycle(
        self,
        user_input=None,
    ):
        """Add a cycle."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            cycle = Cycle(
                id=user_input["id"],
                name=user_input["name"],
                start_date=date.fromisoformat(user_input["start_date"]),
                week_schedule_ids=tuple(user_input["week_schedule_ids"]),
            )

            try:
                runtime.engine.add_cycle(
                    cycle,
                    modified_by="system",
                )
            except ValidationError:
                return self.async_show_form(
                    step_id="add_cycle",
                    data_schema=vol.Schema(
                        {
                            vol.Required("id"): str,
                            vol.Required("name"): str,
                            vol.Required("start_date"): selector.DateSelector(),
                            vol.Required("week_schedule_ids"): selector.SelectSelector(
                                selector.SelectSelectorConfig(
                                    options=[
                                        selector.SelectOptionDict(
                                            value=week_schedule.id,
                                            label=week_schedule.name,
                                        )
                                        for week_schedule in runtime.engine.configuration.week_schedules
                                    ],
                                    multiple=True,
                                    mode=selector.SelectSelectorMode.DROPDOWN,
                                )
                            ),
                        }
                    ),
                    errors={
                        "base": "maximum_cycles_reached",
                    },
                )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        week_options = [
            selector.SelectOptionDict(
                value=week_schedule.id,
                label=week_schedule.name,
            )
            for week_schedule in runtime.engine.configuration.week_schedules
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("name"): str,
                vol.Required("start_date"): selector.DateSelector(),
                vol.Required("week_schedule_ids"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=week_options,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="add_cycle",
            data_schema=schema,
        )

    async def async_step_edit_cycle(
        self,
        user_input=None,
    ):
        """Select a cycle to edit."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_cycle_id = user_input["id"]

            return await self.async_step_edit_cycle_details()

        options = [
            selector.SelectOptionDict(
                value=cycle.id,
                label=cycle.name,
            )
            for cycle in runtime.engine.configuration.cycles
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_cycle",
            data_schema=schema,
        )

    async def async_step_edit_cycle_details(
        self,
        user_input=None,
    ):
        """Edit selected cycle."""

        runtime = self.config_entry.runtime_data

        cycle = runtime.engine.get_cycle(self._selected_cycle_id)

        if user_input is not None:
            updated = Cycle(
                id=cycle.id,
                name=user_input["name"],
                start_date=date.fromisoformat(user_input["start_date"]),
                week_schedule_ids=tuple(user_input["week_schedule_ids"]),
            )

            runtime.engine.update_cycle(
                updated,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        week_options = [
            selector.SelectOptionDict(
                value=week_schedule.id,
                label=week_schedule.name,
            )
            for week_schedule in runtime.engine.configuration.week_schedules
        ]

        schema = vol.Schema(
            {
                vol.Required(
                    "name",
                    default=cycle.name,
                ): str,
                vol.Required(
                    "start_date",
                    default=cycle.start_date.isoformat(),
                ): selector.DateSelector(),
                vol.Required(
                    "week_schedule_ids",
                    default=list(cycle.week_schedule_ids),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=week_options,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_cycle_details",
            data_schema=schema,
        )

    async def async_step_remove_cycle(
        self,
        user_input=None,
    ):
        """Select a cycle to remove."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_remove_cycle_id = user_input["id"]

            return await self.async_step_remove_cycle_confirm()

        options = [
            selector.SelectOptionDict(
                value=cycle.id,
                label=cycle.name,
            )
            for cycle in runtime.engine.configuration.cycles
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_cycle",
            data_schema=schema,
        )

    async def async_step_remove_cycle_confirm(
        self,
        user_input=None,
    ):
        """Confirm cycle removal."""

        runtime = self.config_entry.runtime_data

        cycle = runtime.engine.get_cycle(self._selected_remove_cycle_id)

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_cycle_confirm",
                    data_schema=schema,
                    description_placeholders={
                        "name": cycle.name,
                    },
                )

            runtime.engine.remove_cycle(cycle.id)

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="remove_cycle_confirm",
            data_schema=schema,
            description_placeholders={
                "name": cycle.name,
            },
        )

    async def async_step_add_calendar_exception(
        self,
        user_input=None,
    ):
        """Add a calendar exception."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            calendar_exception = CalendarException(
                id=user_input["id"],
                date=date.fromisoformat(user_input["date"]),
                day_type_id=user_input["day_type_id"],
                description=user_input.get("description") or None,
            )

            runtime.engine.add_calendar_exception(
                calendar_exception,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        day_type_options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in runtime.engine.configuration.day_types
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("date"): selector.DateSelector(),
                vol.Required("day_type_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=day_type_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    "description",
                    default="",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="add_calendar_exception",
            data_schema=schema,
        )

    async def async_step_edit_calendar_exception(
        self,
        user_input=None,
    ):
        """Select a calendar exception to edit."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_calendar_exception_id = user_input["id"]

            return await self.async_step_edit_calendar_exception_details()

        options = [
            selector.SelectOptionDict(
                value=calendar_exception.id,
                label=(
                    calendar_exception.description
                    or calendar_exception.date.isoformat()
                ),
            )
            for calendar_exception in runtime.engine.configuration.calendar_exceptions
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_calendar_exception",
            data_schema=schema,
        )

    async def async_step_edit_calendar_exception_details(
        self,
        user_input=None,
    ):
        """Edit selected calendar exception."""

        runtime = self.config_entry.runtime_data

        calendar_exception = runtime.engine.get_calendar_exception(
            self._selected_calendar_exception_id
        )

        if user_input is not None:
            updated = CalendarException(
                id=calendar_exception.id,
                date=date.fromisoformat(user_input["date"]),
                day_type_id=user_input["day_type_id"],
                description=user_input.get("description") or None,
            )

            runtime.engine.update_calendar_exception(
                updated,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        day_type_options = [
            selector.SelectOptionDict(
                value=day_type.id,
                label=day_type.name,
            )
            for day_type in runtime.engine.configuration.day_types
        ]

        schema = vol.Schema(
            {
                vol.Required(
                    "date",
                    default=calendar_exception.date.isoformat(),
                ): selector.DateSelector(),
                vol.Required(
                    "day_type_id",
                    default=calendar_exception.day_type_id,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=day_type_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    "description",
                    default=calendar_exception.description or "",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="edit_calendar_exception_details",
            data_schema=schema,
        )

    async def async_step_remove_calendar_exception(
        self,
        user_input=None,
    ):
        """Select a calendar exception to remove."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_remove_calendar_exception_id = user_input["id"]

            return await self.async_step_remove_calendar_exception_confirm()

        options = [
            selector.SelectOptionDict(
                value=calendar_exception.id,
                label=(
                    calendar_exception.description
                    or calendar_exception.date.isoformat()
                ),
            )
            for calendar_exception in runtime.engine.configuration.calendar_exceptions
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_calendar_exception",
            data_schema=schema,
        )

    async def async_step_remove_calendar_exception_confirm(
        self,
        user_input=None,
    ):
        """Confirm calendar exception removal."""

        runtime = self.config_entry.runtime_data

        calendar_exception = runtime.engine.get_calendar_exception(
            self._selected_remove_calendar_exception_id
        )

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_calendar_exception_confirm",
                    data_schema=schema,
                    description_placeholders={
                        "name": (
                            calendar_exception.description
                            or calendar_exception.date.isoformat()
                        ),
                    },
                )

            runtime.engine.remove_calendar_exception(calendar_exception.id)

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="remove_calendar_exception_confirm",
            data_schema=schema,
            description_placeholders={
                "name": (
                    calendar_exception.description
                    or calendar_exception.date.isoformat()
                ),
            },
        )

    async def async_step_moment_actions(
        self,
        user_input=None,
    ):
        """Select a moment for action management."""

        runtime = self.config_entry.runtime_data

        if user_input is not None:
            self._selected_action_moment_id = user_input["moment_id"]

            return await self.async_step_moment_actions_menu()

        moments = runtime.engine.configuration.moments

        options = [
            selector.SelectOptionDict(
                value=moment.id,
                label=moment.name,
            )
            for moment in moments
        ]

        schema = vol.Schema(
            {
                vol.Required("moment_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="moment_actions",
            data_schema=schema,
        )

    async def async_step_moment_actions_menu(
        self,
        user_input=None,
    ):
        """Manage actions of the selected moment."""

        return self.async_show_menu(
            step_id="moment_actions_menu",
            menu_options=[
                "add_moment_action",
                "edit_moment_action",
                "remove_moment_action",
            ],
        )

    async def async_step_add_moment_action(
        self,
        user_input=None,
    ):
        """Add an action to the selected moment."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_action_moment_id)

        schema = vol.Schema(
            {
                vol.Required("id"): str,
                vol.Required("label"): str,
                vol.Required("sequence"): selector.ActionSelector(),
            }
        )

        if user_input is not None:
            if not user_input.get("sequence"):
                return self.async_show_form(
                    step_id="add_moment_action",
                    data_schema=schema,
                    errors={
                        "sequence": "action_sequence_required",
                    },
                )

            action = Action(
                id=user_input["id"],
                label=user_input["label"],
                sequence=list(user_input["sequence"]),
            )

            updated_moment = Moment(
                id=moment.id,
                name=moment.name,
                icon=moment.icon,
                actions=(
                    *moment.actions,
                    action,
                ),
            )

            runtime.engine.update_moment(
                updated_moment,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="add_moment_action",
            data_schema=schema,
        )

    async def async_step_edit_moment_action(
        self,
        user_input=None,
    ):
        """Select an action to edit."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_action_moment_id)

        if user_input is not None:
            self._selected_action_id = user_input["id"]

            return await self.async_step_edit_moment_action_details()

        options = [
            selector.SelectOptionDict(
                value=action.id,
                label=f"{action.label} ({action.id})",
            )
            for action in moment.actions
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_moment_action",
            data_schema=schema,
        )

    async def async_step_edit_moment_action_details(
        self,
        user_input=None,
    ):
        """Edit selected action."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_action_moment_id)

        action = next(
            item for item in moment.actions if item.id == self._selected_action_id
        )

        schema = vol.Schema(
            {
                vol.Required(
                    "label",
                    default=action.label,
                ): str,
                vol.Required(
                    "sequence",
                    default=action.sequence,
                ): selector.ActionSelector(),
            }
        )

        if user_input is not None:
            if not user_input.get("sequence"):
                return self.async_show_form(
                    step_id="edit_moment_action_details",
                    data_schema=schema,
                    errors={
                        "sequence": "action_sequence_required",
                    },
                )

            updated_action = Action(
                id=action.id,
                label=user_input["label"],
                sequence=list(user_input["sequence"]),
            )

            actions = tuple(
                updated_action if current.id == action.id else current
                for current in moment.actions
            )

            updated_moment = Moment(
                id=moment.id,
                name=moment.name,
                icon=moment.icon,
                actions=actions,
            )

            runtime.engine.update_moment(
                updated_moment,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="edit_moment_action_details",
            data_schema=schema,
        )

    async def async_step_remove_moment_action(
        self,
        user_input=None,
    ):
        """Select an action to remove."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_action_moment_id)

        if user_input is not None:
            self._selected_remove_action_id = user_input["id"]

            return await self.async_step_remove_moment_action_confirm()

        options = [
            selector.SelectOptionDict(
                value=action.id,
                label=f"{action.label} ({action.id})",
            )
            for action in moment.actions
        ]

        schema = vol.Schema(
            {
                vol.Required("id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="remove_moment_action",
            data_schema=schema,
        )

    async def async_step_remove_moment_action_confirm(
        self,
        user_input=None,
    ):
        """Confirm action removal."""

        runtime = self.config_entry.runtime_data

        moment = runtime.engine.get_moment(self._selected_action_moment_id)

        action = next(
            item
            for item in moment.actions
            if item.id == self._selected_remove_action_id
        )

        schema = vol.Schema(
            {
                vol.Required(
                    "confirm",
                    default=False,
                ): bool,
            }
        )

        if user_input is not None:
            if not user_input["confirm"]:
                return self.async_show_form(
                    step_id="remove_moment_action_confirm",
                    data_schema=schema,
                    description_placeholders={
                        "name": action.label,
                    },
                )

            actions = tuple(
                current for current in moment.actions if current.id != action.id
            )

            updated_moment = Moment(
                id=moment.id,
                name=moment.name,
                icon=moment.icon,
                actions=actions,
            )

            runtime.engine.update_moment(
                updated_moment,
                modified_by="system",
            )

            await runtime.async_configuration_updated()

            return self.async_create_entry(
                title="",
                data=self.config_entry.options,
            )

        return self.async_show_form(
            step_id="remove_moment_action_confirm",
            data_schema=schema,
            description_placeholders={
                "name": action.label,
            },
        )
