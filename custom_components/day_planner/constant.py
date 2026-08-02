DOMAIN = "day_planner"

STORAGE_VERSION = 1
STORAGE_KEY = "day_planner"

PLATFORMS = [
    "sensor",
    "calendar",
]

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
