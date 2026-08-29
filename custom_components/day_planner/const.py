DOMAIN = "day_planner"

NAME = "Day Planner"

INTEGRATION_NAME = NAME 

RELEASE_URL = "https://github.com/fmo01/hass-day_planner/releases"

VERSION = "0.0.2"

SIGNAL_PLANNER_UPDATED = "day_planner_updated"

STORAGE_VERSION = 1
STORAGE_KEY = "day_planner.storage"

CONF_DELETE_DATA_ON_REMOVE = "delete_data_on_remove"

DEFAULT_DELETE_DATA_ON_REMOVE = False

PLATFORMS = [
    "sensor",
    "calendar",
]

SERVICE_ADD_MOMENT = "add_moment"
SERVICE_UPDATE_MOMENT = "update_moment"
SERVICE_REMOVE_MOMENT = "remove_moment"
SERVICE_ADD_DAY_TYPE = "add_day_type"
SERVICE_UPDATE_DAY_TYPE = "update_day_type"
SERVICE_REMOVE_DAY_TYPE = "remove_day_type"
SERVICE_ADD_SCHEDULED_MOMENT = "add_scheduled_moment"
SERVICE_UPDATE_SCHEDULED_MOMENT = "update_scheduled_moment"
SERVICE_REMOVE_SCHEDULED_MOMENT = "remove_scheduled_moment"
SERVICE_ADD_WEEK_SCHEDULE = "add_week_schedule"
SERVICE_UPDATE_WEEK_SCHEDULE = "update_week_schedule"
SERVICE_REMOVE_WEEK_SCHEDULE = "remove_week_schedule"
SERVICE_ADD_CYCLE = "add_cycle"
SERVICE_UPDATE_CYCLE = "update_cycle"
SERVICE_REMOVE_CYCLE = "remove_cycle"
SERVICE_ADD_CALENDAR_EXCEPTION = "add_calendar_exception"
SERVICE_UPDATE_CALENDAR_EXCEPTION = "update_calendar_exception"
SERVICE_REMOVE_CALENDAR_EXCEPTION = "remove_calendar_exception"


DEFAULT_MOMENTS = [
    {
        "id": "wake_up",
        "name": "Réveil",
        "icon": "mdi:weather-sunset-up",
    },
    {
        "id": "leave",
        "name": "Départ",
        "icon": "mdi:car",
    },
    {
        "id": "return",
        "name": "Retour",
        "icon": "mdi:home",
    },
    {
        "id": "evening",
        "name": "Soir",
        "icon": "mdi:weather-night",
    },
    {
        "id": "bedtime",
        "name": "Coucher",
        "icon": "mdi:sleep",
    },
    {
        "id": "night",
        "name": "Nuit",
        "icon": "mdi:moon-waning-crescent",
    },
]
