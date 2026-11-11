"""Unit tests for the one-time eedomus agenda import builder."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from custom_components.day_planner.domain.day_type import DayType
from custom_components.day_planner.domain.planner_configuration import (
    PlannerConfiguration,
)
from custom_components.day_planner.eedomus_import import (
    EedomusImportError,
    get_eedomus_entity_map,
)
from custom_components.day_planner.eedomus_import import (
    create_import_plan as _create_import_plan,
)

BOX = "01KWFVW58SZD6W6WHB5YRHNDY9"
BOX_NAME = "Eedomus (192.20.55.30)"
ID_PREFIX = f"eedomus_{BOX_NAME}_"


def create_import_plan(*args, **kwargs):
    """Test helper: every imported Day Planner object is named after its box."""
    kwargs.setdefault("week_name", BOX_NAME)
    return _create_import_plan(*args, **kwargs)


def make_agenda():
    """A repeated phase must produce distinct scheduled moments."""
    return {
        "phases": [{"id": 5, "name": "Couché"}],
        "day_types": [
            {
                "id": 1,
                "name": "Journée de travail",
                "moments": [
                    {
                        "phase_id": 5,
                        "phase": "Couché",
                        "heure": f"{hour:02d}:00:00",
                        "regle_horaire_id": str(hour),
                        "regle_horaire_active": True,
                        "regle_actions_id": "1",
                        "regle_actions_active": True,
                        "actions": [
                            {
                                "type_action": "direct",
                                "peripherique_id": "3463520",
                                "peripherique": "Thermostat Salle a manger",
                                "valeur": "22.5",
                                "etat": "22.5°C",
                                "quoi_faire": "Thermostat Salle a manger → 22.5°C",
                            }
                        ],
                    }
                    for hour in (0, 6, 8)
                ],
            }
        ],
        "week": [{"jour_numero": i, "type_journee_id": 1} for i in range(1, 8)],
        "regles_conditionnelles_liees_agenda": [{"active": True}],
        "parametres_embarques_non_resolus": [],
    }


def mappings():
    return {"3463520": [SimpleNamespace(entity_id="climate.thermostat_salle_a_manger", disabled_by=None)]}


def test_create_one_time_import_with_repeated_phase():
    plan = create_import_plan(
        make_agenda(),
        PlannerConfiguration.empty(),
        BOX,
        mappings(),
        actor="Utilisateur Test",
    )
    assert plan.day_types == 1
    assert plan.moments == 3
    assert plan.scheduled == 3
    assert plan.actions == 3
    assert plan.conditional_rules_not_imported == 1
    cfg = plan.configuration
    assert len(cfg.cycles) == len(cfg.calendar_exceptions) == 0
    assert cfg.week_schedules[0].name == BOX_NAME
    assert cfg.day_types[0].name == f"Journée de travail — {BOX_NAME}"
    assert len({s.moment_id for s in cfg.day_types[0].scheduled_moments}) == 3
    assert cfg.moments[0].audit.created_by == "Utilisateur Test"
    for m in cfg.moments:
        assert m.actions[0].sequence == [
            {
                "action": "climate.set_temperature",
                "target": {"entity_id": "climate.thermostat_salle_a_manger"},
                "data": {"temperature": 22.5},
            }
        ]


def test_replace_requires_explicit_approval_and_preserves_unrelated_data():
    first = create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mappings())
    unrelated = DayType(id="manual", name="Manuelle", scheduled_moments=())
    current = replace(first.configuration, day_types=(*first.configuration.day_types, unrelated))
    with pytest.raises(EedomusImportError, match="confirmation"):
        create_import_plan(make_agenda(), current, BOX, mappings())
    updated = create_import_plan(
        make_agenda(),
        current,
        BOX,
        mappings(),
        replace_existing=True,
        actor="Autre utilisateur",
    )
    assert len(updated.configuration.day_types) == 2
    assert unrelated in updated.configuration.day_types
    old = first.configuration.moments[0].audit
    new = updated.configuration.moments[0].audit
    assert new.created_by == old.created_by
    assert new.created_at == old.created_at
    assert new.modified_by == "Autre utilisateur"


def test_missing_mapping_blocks_all_changes():
    with pytest.raises(EedomusImportError, match="0 entité"):
        create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, {})


def test_ambiguous_mapping_blocks_all_changes():
    mapping = mappings()
    mapping["3463520"].append(SimpleNamespace(entity_id="climate.second", disabled_by=None))
    with pytest.raises(EedomusImportError, match="2 entité"):
        create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mapping)


def test_inactive_rule_blocks_import():
    sample = make_agenda()
    sample["day_types"][0]["moments"][0]["regle_horaire_active"] = False
    with pytest.raises(EedomusImportError, match="désactivée"):
        create_import_plan(sample, PlannerConfiguration.empty(), BOX, mappings())


def test_incoherent_phase_actions_block_import():
    sample = make_agenda()
    sample["day_types"][0]["moments"][1]["actions"][0]["valeur"] = "24"
    with pytest.raises(EedomusImportError, match="incohérentes"):
        create_import_plan(sample, PlannerConfiguration.empty(), BOX, mappings())


def test_unsupported_sensor_preserves_repeated_moments_and_all_schedules():
    """Only a sensor exists: skip the command, but create every moment/time."""
    mapping = {"3463520": [SimpleNamespace(entity_id="sensor.unknown", disabled_by=None)]}
    plan = create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mapping)
    assert plan.actions == 0
    assert plan.moments == plan.scheduled == 3
    assert plan.moments_without_actions == 3
    assert all(not moment.actions for moment in plan.configuration.moments)
    assert len(plan.configuration.day_types[0].scheduled_moments) == 3
    assert plan.unsupported_associations == (
        (
            "Thermostat Salle a manger [3463520]",
            "sensor.unknown",
            "Domaine sensor non pris en charge",
        ),
    )


def test_other_unsupported_domains_are_skipped_without_blocking():
    """All non-command domains are informative, including binary_sensor."""
    mapping = {"3463520": [SimpleNamespace(entity_id="binary_sensor.motion", disabled_by=None)]}
    plan = create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mapping)
    assert plan.moments == 3 and plan.actions == 0
    assert plan.unsupported_associations[0][1] == "binary_sensor.motion"
    assert "binary_sensor" in plan.unsupported_associations[0][2]


def test_supported_target_wins_without_hiding_unsupported_association():
    mapping = mappings()
    mapping["3463520"].append(SimpleNamespace(entity_id="sensor.thermostat_status", disabled_by=None))
    plan = create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mapping)
    assert plan.actions == 3
    assert len(plan.unsupported_associations) == 1
    assert plan.unsupported_associations[0][1] == "sensor.thermostat_status"


def test_unsupported_service_value_does_not_prevent_moment_creation():
    agenda = make_agenda()
    for scheduled in agenda["day_types"][0]["moments"]:
        scheduled["actions"][0]["valeur"] = "not-a-temperature"
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), BOX, mappings())
    assert plan.actions == 0
    assert plan.moments == plan.scheduled == 3
    assert len(plan.unsupported_associations) == 1
    assert "Consigne chauffage invalide" in plan.unsupported_associations[0][2]


def test_unsupported_macro_does_not_require_entity_mapping():
    agenda = make_agenda()
    for scheduled in agenda["day_types"][0]["moments"]:
        scheduled["actions"][0]["type_action"] = "macro"
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), BOX, {})
    assert plan.actions == 0 and plan.moments == 3
    assert plan.unsupported_associations[0][1] == "—"
    assert "macro" in plan.unsupported_associations[0][2]


def test_phase_with_no_active_actions_still_imports_empty_moments():
    agenda = make_agenda()
    for scheduled in agenda["day_types"][0]["moments"]:
        scheduled["regle_actions_active"] = False
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), BOX, {})
    assert plan.moments == plan.scheduled == 3
    assert plan.actions == 0
    assert plan.moments_without_actions == 3
    assert plan.unsupported_associations == ()
    assert len(plan.configuration.day_types[0].scheduled_moments) == 3


def test_partial_unsupported_commands_preserve_compatible_action():
    agenda = make_agenda()
    extra = {
        "type_action": "direct",
        "peripherique_id": "10",
        "peripherique": "Volet",
        "valeur": "100",
        "etat": "Ouvert",
        "quoi_faire": "Volet → Ouvert",
    }
    for scheduled in agenda["day_types"][0]["moments"]:
        scheduled["actions"].append(extra.copy())
    mapping = {
        "3463520": [SimpleNamespace(entity_id="sensor.thermostat", disabled_by=None)],
        "10": [SimpleNamespace(entity_id="cover.volet", disabled_by=None)],
    }
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), BOX, mapping)
    assert plan.actions == 3
    assert plan.moments_without_actions == 0
    assert all(len(m.actions) == 1 for m in plan.configuration.moments)
    assert all(m.actions[0].sequence[0]["action"] == "cover.open_cover" for m in plan.configuration.moments)
    assert len(plan.unsupported_associations) == 1


def test_disabled_entity_blocks_import():
    mapping = mappings()
    mapping["3463520"][0].disabled_by = "user"
    with pytest.raises(EedomusImportError, match="désactivée"):
        create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mapping)


def test_action_cover_and_light_conversions():
    agenda = make_agenda()
    base = agenda["day_types"][0]["moments"][0]
    # Use another phase, rather than changing the action list of the same phase.
    base["actions"] = [
        {
            "type_action": "direct",
            "peripherique_id": "10",
            "peripherique": "Volet",
            "valeur": "100",
            "etat": "Ouvert",
            "quoi_faire": "Volet → Ouvert",
        },
        {
            "type_action": "direct",
            "peripherique_id": "11",
            "peripherique": "Guirlande",
            "valeur": "0",
            "etat": "Off",
            "quoi_faire": "Guirlande → Off",
        },
    ]
    agenda["day_types"][0]["moments"] = [base]
    mapping = {
        "10": [SimpleNamespace(entity_id="cover.volet", disabled_by=None)],
        "11": [SimpleNamespace(entity_id="light.guirlande", disabled_by=None)],
    }
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), BOX, mapping)
    seq = [action.sequence[0]["action"] for action in plan.configuration.moments[0].actions]
    assert seq == ["cover.open_cover", "light.turn_off"]


def test_entity_registry_accepts_unique_id_with_and_without_domain_suffix():
    """The HA eedomus entity registry supports both historical ID shapes."""
    entries = [
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_3463520_climate",
            platform="eedomus",
            entity_id="climate.thermostat_salle_a_manger",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_795317",
            platform="eedomus",
            entity_id="cover.volet_sejour",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_34635201_climate",
            platform="eedomus",
            entity_id="climate.other",
        ),
        SimpleNamespace(
            unique_id="eedomus_ANOTHER_795317_cover",
            platform="eedomus",
            entity_id="cover.other_box",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_795535_light",
            platform="different",
            entity_id="light.other_platform",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_3463520_battery",
            platform="eedomus",
            entity_id="sensor.thermostat_battery",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_795317_sensor_battery",
            platform="eedomus",
            entity_id="sensor.volet_battery",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_24680_battery_level",
            platform="eedomus",
            entity_id="sensor.another_battery_level",
        ),
    ]
    with (
        patch("homeassistant.helpers.entity_registry.async_get", return_value=MagicMock()),
        patch(
            "homeassistant.helpers.entity_registry.async_entries_for_config_entry",
            return_value=entries,
        ) as lookup,
    ):
        mapped = get_eedomus_entity_map(MagicMock(), BOX)
    assert sorted(mapped) == ["3463520", "34635201", "795317"]
    assert mapped["795317"][0].entity_id == "cover.volet_sejour"
    assert mapped["3463520"][0].entity_id == "climate.thermostat_salle_a_manger"
    lookup.assert_called_once()


def test_registry_accepts_optional_eedomus_prefix_with_optional_type_suffix():
    """All four valid unique_id layouts must resolve to the correct module."""
    entries = [
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_10001_climate",
            platform="eedomus",
            entity_id="climate.with_prefix_and_suffix",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_10002",
            platform="eedomus",
            entity_id="switch.with_prefix_only",
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_10003_cover",
            platform="eedomus",
            entity_id="cover.without_prefix_with_suffix",
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_10004",
            platform="eedomus",
            entity_id="light.without_prefix_or_suffix",
        ),
        # Different box, wrong platform, and numeric-prefix matches are invalid.
        SimpleNamespace(
            unique_id="ANOTHER_10005_cover",
            platform="eedomus",
            entity_id="cover.other_box",
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_10005_light",
            platform="different",
            entity_id="light.other_platform",
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_100045_cover",
            platform="eedomus",
            entity_id="cover.neighboring_numeric_id",
        ),
        # Battery sensors must be ignored in both naming conventions.
        SimpleNamespace(
            unique_id=f"{BOX}_10003_battery",
            platform="eedomus",
            entity_id="sensor.cover_battery",
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_10004_sensor_battery",
            platform="eedomus",
            entity_id="sensor.light_battery",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_10002_battery_level",
            platform="eedomus",
            entity_id="sensor.switch_battery",
        ),
    ]
    with (
        patch("homeassistant.helpers.entity_registry.async_get", return_value=MagicMock()),
        patch(
            "homeassistant.helpers.entity_registry.async_entries_for_config_entry",
            return_value=entries,
        ) as lookup,
    ):
        mapped = get_eedomus_entity_map(MagicMock(), BOX)
    assert {key: [entity.entity_id for entity in value] for key, value in mapped.items()} == {
        "10001": ["climate.with_prefix_and_suffix"],
        "10002": ["switch.with_prefix_only"],
        "10003": ["cover.without_prefix_with_suffix"],
        "10004": ["light.without_prefix_or_suffix"],
        "100045": ["cover.neighboring_numeric_id"],
    }
    lookup.assert_called_once()
    assert lookup.call_args.args[1] == BOX


def test_active_box_sensor_without_eedomus_prefix_is_reported_not_imported():
    """Regression: HA active sensor for 795317 is shown as incompatible."""
    active = "01M6GZYTTC6861DDKK9EBZX1E5"
    entities = [
        SimpleNamespace(
            unique_id=f"{active}_795317",
            platform="eedomus",
            entity_id="sensor.cmd_1_volet_sejour_salle_a_manger",
            disabled_by=None,
        ),
        # An old orphaned switch belongs to a different config entry.
        SimpleNamespace(
            unique_id="eedomus_01KT16AM2N9AZKCYJCKRJR6M3H_795317",
            platform="eedomus",
            entity_id="switch.cmd_1_volet_sejour_salle_a_manger",
            disabled_by=None,
        ),
    ]
    with (
        patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=MagicMock(),
        ),
        patch(
            "homeassistant.helpers.entity_registry.async_entries_for_config_entry",
            return_value=entities,
        ),
    ):
        mapped = get_eedomus_entity_map(MagicMock(), active)
    assert [entry.entity_id for entry in mapped["795317"]] == ["sensor.cmd_1_volet_sejour_salle_a_manger"]
    agenda = make_agenda()
    for moment in agenda["day_types"][0]["moments"]:
        moment["actions"][0].update(
            {
                "peripherique_id": "795317",
                "peripherique": "Cmd 1 Volet Séjour",
                "valeur": "100",
                "etat": "Ouvert",
                "quoi_faire": "Cmd 1 Volet Séjour → Ouvert",
            }
        )
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), active, mapped)
    assert plan.actions == 0
    assert plan.moments == plan.scheduled == 3
    assert plan.unsupported_associations == (
        (
            "Cmd 1 Volet Séjour [795317]",
            "sensor.cmd_1_volet_sejour_salle_a_manger",
            "Domaine sensor non pris en charge",
        ),
    )


def test_registry_mixed_prefixes_do_not_hide_ambiguous_entities():
    """If two main entities share a module ID, the importer still refuses."""
    entries = [
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_3463520_climate",
            platform="eedomus",
            entity_id="climate.thermostat_a",
            disabled_by=None,
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_3463520",
            platform="eedomus",
            entity_id="switch.thermostat_b",
            disabled_by=None,
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_3463520_battery",
            platform="eedomus",
            entity_id="sensor.thermostat_battery",
            disabled_by=None,
        ),
    ]
    with (
        patch("homeassistant.helpers.entity_registry.async_get", return_value=MagicMock()),
        patch(
            "homeassistant.helpers.entity_registry.async_entries_for_config_entry",
            return_value=entries,
        ),
    ):
        mapping = get_eedomus_entity_map(MagicMock(), BOX)
    assert len(mapping["3463520"]) == 2
    with pytest.raises(EedomusImportError, match="2 entité"):
        create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mapping)


def test_registry_excludes_battery_without_losing_valid_device():
    """Battery sensors must not compete with the actuator for one module ID."""
    entries = [
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_12345_battery",
            platform="eedomus",
            entity_id="sensor.device_battery",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_12345_cover",
            platform="eedomus",
            entity_id="cover.shutter",
            disabled_by=None,
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_98765_battery",
            platform="eedomus",
            entity_id="sensor.other_battery",
        ),
        SimpleNamespace(
            unique_id=f"eedomus_{BOX}_77777",
            platform="eedomus",
            entity_id="switch.plug",
            disabled_by=None,
        ),
    ]
    with (
        patch("homeassistant.helpers.entity_registry.async_get", return_value=MagicMock()),
        patch(
            "homeassistant.helpers.entity_registry.async_entries_for_config_entry",
            return_value=entries,
        ),
    ):
        mapped = get_eedomus_entity_map(MagicMock(), BOX)
    assert sorted(mapped) == ["12345", "77777"]
    assert [entity.entity_id for entity in mapped["12345"]] == ["cover.shutter"]
    assert [entity.entity_id for entity in mapped["77777"]] == ["switch.plug"]


def test_import_with_no_repeated_phase():
    """The newest export has one phase occurrence per day: no clone is needed."""
    agenda = make_agenda()
    agenda["day_types"][0]["moments"] = agenda["day_types"][0]["moments"][:1]
    plan = create_import_plan(agenda, PlannerConfiguration.empty(), BOX, mappings())
    assert plan.day_types == 1
    assert plan.moments == plan.scheduled == plan.actions == 1
    assert plan.configuration.moments[0].id == f"{ID_PREFIX}phase_5"


def test_binary_switch_accepts_eedomus_roller_shutter_open_and_closed():
    """eedomus utilisation 109 can expose 100/Ouvert as a switch in HA."""
    from custom_components.day_planner.eedomus_import import _convert_service

    target = SimpleNamespace(entity_id="switch.cmd_1_volet_sejour")
    raw = {
        "type_action": "direct",
        "peripherique": "Cmd 1 Volet Séjour",
        "peripherique_id": "795317",
        "valeur": "100",
        "etat": "Ouvert",
    }
    opened = _convert_service(raw, target)
    assert opened == {
        "action": "switch.turn_on",
        "target": {"entity_id": target.entity_id},
    }
    closed = _convert_service({**raw, "valeur": "0", "etat": "Fermé"}, target)
    assert closed == {
        "action": "switch.turn_off",
        "target": {"entity_id": target.entity_id},
    }


def test_binary_light_accepts_eedomus_roller_shutter_labels():
    from custom_components.day_planner.eedomus_import import _convert_service

    target = SimpleNamespace(entity_id="light.cmd_1_volet_sejour")
    raw = {
        "type_action": "direct",
        "peripherique": "Cmd 1 Volet Séjour",
        "peripherique_id": "795317",
        "valeur": "100",
        "etat": "Ouvert",
    }
    assert _convert_service(raw, target)["action"] == "light.turn_on"
    assert _convert_service({**raw, "valeur": "0", "etat": "Fermée"}, target)["action"] == "light.turn_off"


def test_unknown_binary_state_reports_entity_device_and_expected_values():
    from custom_components.day_planner.eedomus_import import _convert_service

    raw = {
        "type_action": "direct",
        "peripherique": "Cmd 1 Volet Séjour",
        "peripherique_id": "795317",
        "valeur": "80",
        "etat": "partiel",
    }
    with pytest.raises(EedomusImportError) as info:
        _convert_service(raw, SimpleNamespace(entity_id="switch.cmd_1_volet_sejour"))
    message = str(info.value)
    for content in (
        "Cmd 1 Volet Séjour",
        "795317",
        "switch.cmd_1_volet_sejour",
        "80",
        "partiel",
        "100/Ouvert",
    ):
        assert content in message


def test_week_uses_selected_box_name_for_display_and_id():
    """The readable box name replaces the HA entry ID in Day Planner IDs."""
    box_name = "Eedomus (192.20.55.30)"
    plan = create_import_plan(
        make_agenda(),
        PlannerConfiguration.empty(),
        BOX,
        mappings(),
        week_name=box_name,
    )
    imported_week = plan.configuration.week_schedules[0]
    assert imported_week.name == box_name
    assert imported_week.id == f"{ID_PREFIX}week"

    replaced = create_import_plan(
        make_agenda(),
        plan.configuration,
        BOX,
        mappings(),
        replace_existing=True,
        week_name=box_name,
    )
    assert replaced.had_previous_import
    assert replaced.configuration.week_schedules[0].name == box_name
    assert replaced.configuration.week_schedules[0].id == imported_week.id


def test_all_created_display_names_use_selected_box_name():
    """Week, day types, moments (including repeats), and actions share the box name."""
    box_name = "Eedomus (192.20.55.30)"
    plan = create_import_plan(
        make_agenda(),
        PlannerConfiguration.empty(),
        BOX,
        mappings(),
        week_name=box_name,
    )
    config = plan.configuration
    assert config.week_schedules[0].name == box_name
    assert config.day_types[0].name == f"Journée de travail — {box_name}"
    assert {moment.name for moment in config.moments} == {
        f"Couché — {box_name}",
        f"Couché (occurrence 2) — {box_name}",
        f"Couché (occurrence 3) — {box_name}",
    }
    assert all(
        action.label == f"Thermostat Salle a manger → 22.5°C — {box_name}"
        for moment in config.moments
        for action in moment.actions
    )
    # Every Day Planner ID incorporates the full human-readable box name.
    imported = (*config.moments, *config.day_types, *config.week_schedules)
    assert all(item.id.startswith(ID_PREFIX) for item in imported)
    assert all(BOX not in item.id for item in imported)
    assert all(action.id.startswith(ID_PREFIX) for moment in config.moments for action in moment.actions)


def test_reimport_same_box_name_preserves_ids_and_audit():
    """A replacement of the same box retains IDs and creation metadata."""
    original = create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mappings())
    revised = create_import_plan(
        make_agenda(),
        original.configuration,
        BOX,
        mappings(),
        replace_existing=True,
        actor="Autre utilisateur",
    )
    assert revised.had_previous_import
    for collection in ("week_schedules", "day_types", "moments"):
        assert [obj.id for obj in getattr(original.configuration, collection)] == [
            obj.id for obj in getattr(revised.configuration, collection)
        ]
    assert all(
        old.audit.created_at == new.audit.created_at
        for old, new in zip(original.configuration.moments, revised.configuration.moments)
    )
    assert all(item.audit.modified_by == "Autre utilisateur" for item in revised.configuration.moments)


def test_replaces_legacy_entry_id_import_after_confirmation():
    """An old v5.x import is removed when migrated to IP-based IDs."""
    original = create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mappings())
    legacy_prefix = f"eedomus_{BOX}_"

    def legacy_id(value):
        assert value.startswith(ID_PREFIX)
        return legacy_prefix + value.removeprefix(ID_PREFIX)

    cfg = original.configuration
    legacy_moments = tuple(
        replace(
            item,
            id=legacy_id(item.id),
            actions=tuple(replace(action, id=legacy_id(action.id)) for action in item.actions),
        )
        for item in cfg.moments
    )
    legacy_days = tuple(
        replace(
            item,
            id=legacy_id(item.id),
            scheduled_moments=tuple(
                replace(scheduled, moment_id=legacy_id(scheduled.moment_id)) for scheduled in item.scheduled_moments
            ),
        )
        for item in cfg.day_types
    )
    legacy_weeks = tuple(
        replace(
            item,
            id=legacy_id(item.id),
            **{
                weekday: legacy_id(getattr(item, weekday))
                for weekday in (
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                )
            },
        )
        for item in cfg.week_schedules
    )
    before = replace(
        cfg,
        moments=legacy_moments,
        day_types=legacy_days,
        week_schedules=legacy_weeks,
    )
    with pytest.raises(EedomusImportError, match="confirmation"):
        create_import_plan(make_agenda(), before, BOX, mappings())
    updated = create_import_plan(
        make_agenda(),
        before,
        BOX,
        mappings(),
        replace_existing=True,
        actor="Auteur remplaçant",
    )
    assert updated.had_previous_import
    for kind in ("moments", "day_types", "week_schedules"):
        objects = getattr(updated.configuration, kind)
        assert all(item.id.startswith(ID_PREFIX) for item in objects)
        assert all(not item.id.startswith(legacy_prefix) for item in objects)
        assert all(item.audit.created_by == "system" for item in objects)
        assert all(item.audit.modified_by == "Auteur remplaçant" for item in objects)


def test_missing_box_name_prevents_id_generation():
    """Never create fallback IDs that omit the selected box address."""
    with pytest.raises(EedomusImportError, match="Nom de box eedomus"):
        _create_import_plan(
            make_agenda(),
            PlannerConfiguration.empty(),
            BOX,
            mappings(),
        )


def test_same_box_address_two_config_entries_does_not_change_ha_mapping():
    """HA registry matching still relies on entry_id, not on the display name."""
    plan = create_import_plan(
        make_agenda(),
        PlannerConfiguration.empty(),
        BOX,
        mappings(),
    )
    assert plan.source_entry_id == BOX
    assert plan.configuration.moments[0].id.startswith(ID_PREFIX)
    assert BOX not in plan.configuration.moments[0].id


def test_remaining_service_conversion_paths_and_invalid_source_ids():
    """Close-cover, binary on, invalid commands and host-independent IDs."""
    from custom_components.day_planner import eedomus_import as impl

    with pytest.raises(EedomusImportError, match="Identifiant"):
        impl._legacy_namespace("not a valid entry id")

    raw = {
        "peripherique": "Volet",
        "peripherique_id": "123",
        "type_action": "macro",
        "valeur": "0",
        "etat": "Fermé",
    }
    with pytest.raises(EedomusImportError, match="non directe"):
        impl._convert_service(raw, SimpleNamespace(entity_id="cover.test"))

    raw["type_action"] = "direct"
    assert impl._convert_service(raw, SimpleNamespace(entity_id="cover.volet"))["action"] == "cover.close_cover"
    raw.update(valeur="99", etat="intermédiaire")
    with pytest.raises(EedomusImportError, match="Commande volet non reconnue"):
        impl._convert_service(raw, SimpleNamespace(entity_id="cover.volet"))

    raw.update(valeur="100", etat="On")
    assert impl._convert_service(raw, SimpleNamespace(entity_id="light.guide"))["action"] == "light.turn_on"
    with pytest.raises(EedomusImportError, match="non prise en charge"):
        impl._convert_service(raw, SimpleNamespace(entity_id="sensor.guide"))

    raw.update(valeur="81", etat="81°C")
    with pytest.raises(EedomusImportError, match="hors limite"):
        impl._convert_service(raw, SimpleNamespace(entity_id="climate.guide"))


def test_registry_ignores_nonnumeric_device_unique_ids():
    from homeassistant.helpers import entity_registry as er

    entries = [
        SimpleNamespace(
            unique_id=f"{BOX}_ABC_switch",
            platform="eedomus",
            entity_id="switch.invalid",
        ),
        SimpleNamespace(
            unique_id=f"{BOX}_1_extra-characters",
            platform="eedomus",
            entity_id="switch.other",
        ),
    ]
    with (
        patch.object(er, "async_get", return_value=MagicMock()),
        patch.object(er, "async_entries_for_config_entry", return_value=entries),
    ):
        assert get_eedomus_entity_map(MagicMock(), BOX) == {}


def test_validation_of_week_and_planner_raises_explicit_import_errors():
    from custom_components.day_planner import eedomus_import as impl
    from custom_components.day_planner.planner.errors import ValidationError

    agenda = make_agenda()
    agenda["week"] = agenda["week"][:-1]
    with pytest.raises(EedomusImportError, match="sept jours"):
        create_import_plan(agenda, PlannerConfiguration.empty(), BOX, mappings())

    with patch.object(
        impl.PlannerValidator,
        "validate_configuration",
        side_effect=ValidationError("cycle invalide"),
    ):
        with pytest.raises(
            EedomusImportError,
            match="Configuration Day Planner incompatible : cycle invalide",
        ):
            create_import_plan(make_agenda(), PlannerConfiguration.empty(), BOX, mappings())


def test_merging_without_explicit_confirmation_preserves_unrelated_objects():
    from custom_components.day_planner import eedomus_import as impl

    manual = SimpleNamespace(id="manual")
    previous = SimpleNamespace(id="eedomus_old_week")
    with pytest.raises(EedomusImportError, match="confirmation"):
        impl._merged((manual, previous), [SimpleNamespace(id="new")], ("eedomus_old_",), False)
    merged = impl._merged((manual, previous), [SimpleNamespace(id="new")], ("eedomus_old_",), True)
    assert [item.id for item in merged] == ["manual", "new"]


def test_prepare_import_calls_extractor_after_json_read(tmp_path):
    from custom_components.day_planner import eedomus_import as impl

    input_path = tmp_path / "eedomus.json"
    input_path.write_text('{"tables": []}', encoding="utf-8")
    expected = {"day_types": []}
    with patch.object(impl, "extract", return_value=expected) as extract_mock:
        assert impl.prepare_import(MagicMock(), BOX, input_path) == expected
    extract_mock.assert_called_once_with({"tables": []})
