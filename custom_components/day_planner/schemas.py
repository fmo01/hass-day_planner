import voluptuous as vol
from homeassistant.helpers import config_validation as cv

ACTION_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("sequence"): list,
    }
)

ADD_MOMENT_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("name"): cv.string,
        vol.Optional(
            "icon",
            default=None,
        ): vol.Any(
            cv.string,
            None,
        ),
        vol.Optional(
            "actions",
            default=[],
        ): [ACTION_SCHEMA],
    }
)

UPDATE_MOMENT_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("name"): cv.string,
        vol.Optional(
            "icon",
            default=None,
        ): vol.Any(
            cv.string,
            None,
        ),
        vol.Optional(
            "actions",
        ): [ACTION_SCHEMA],
    }
)

REMOVE_MOMENT_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
    }
)

ADD_DAY_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): str,
        vol.Required("name"): str,
    }
)

UPDATE_DAY_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): str,
        vol.Required("name"): str,
    }
)

REMOVE_DAY_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): str,
    }
)

ADD_WEEK_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): str,
        vol.Required("name"): str,
        vol.Required("monday"): str,
        vol.Required("tuesday"): str,
        vol.Required("wednesday"): str,
        vol.Required("thursday"): str,
        vol.Required("friday"): str,
        vol.Required("saturday"): str,
        vol.Required("sunday"): str,
    }
)

UPDATE_WEEK_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): str,
        vol.Required("name"): str,
        vol.Required("monday"): str,
        vol.Required("tuesday"): str,
        vol.Required("wednesday"): str,
        vol.Required("thursday"): str,
        vol.Required("friday"): str,
        vol.Required("saturday"): str,
        vol.Required("sunday"): str,
    }
)

REMOVE_WEEK_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): str,
    }
)

ADD_CYCLE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("name"): cv.string,
        vol.Required("start_date"): cv.string,
        vol.Required("week_schedule_ids"): [cv.string],
    }
)

UPDATE_CYCLE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("name"): cv.string,
        vol.Required("start_date"): cv.string,
        vol.Required("week_schedule_ids"): [cv.string],
    }
)

REMOVE_CYCLE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
    }
)

ADD_CALENDAR_EXCEPTION_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("date"): cv.string,
        vol.Required("day_type_id"): cv.string,
        vol.Optional(
            "description",
            default=None,
        ): vol.Any(
            cv.string,
            None,
        ),
    }
)

UPDATE_CALENDAR_EXCEPTION_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
        vol.Required("date"): cv.string,
        vol.Required("day_type_id"): cv.string,
        vol.Optional(
            "description",
            default=None,
        ): vol.Any(
            cv.string,
            None,
        ),
    }
)

REMOVE_CALENDAR_EXCEPTION_SCHEMA = vol.Schema(
    {
        vol.Required("id"): cv.string,
    }
)

ADD_SCHEDULED_MOMENT_SCHEMA = vol.Schema(
    {
        vol.Required("day_type_id"): cv.string,
        vol.Required("moment_id"): cv.string,
        vol.Required("time"): cv.string,
    }
)

UPDATE_SCHEDULED_MOMENT_SCHEMA = vol.Schema(
    {
        vol.Required("day_type_id"): cv.string,
        vol.Required("moment_id"): cv.string,
        vol.Required("time"): cv.string,
    }
)


REMOVE_SCHEDULED_MOMENT_SCHEMA = vol.Schema(
    {
        vol.Required("day_type_id"): cv.string,
        vol.Required("moment_id"): cv.string,
    }
)
