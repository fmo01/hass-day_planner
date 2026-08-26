# Day Planner — Documentation technique

**Version de référence : 0.0.x**

## 1. Architecture

```text
Home Assistant
       │
       ├── Config Flow
       ├── Options Flow
       ├── Services
       │
       ▼
   Runtime
       │
       ▼
 PlannerEngine
       │
       ├── Domain objects
       └── PlannerValidator
       │
       ▼
 DayPlannerStorage
       │
       ▼
 .storage/day_planner_configuration
```

Le domaine métier est séparé des mécanismes Home Assistant afin de permettre des tests unitaires indépendants.

## 2. Arborescence

```text
custom_components/day_planner/
├── __init__.py
├── config_flow.py
├── options_flow.py
├── const.py
├── runtime.py
├── schemas.py
├── services.py
├── storage.py
├── domain/
│   ├── __init__.py
│   ├── action.py
│   ├── calendar_exception.py
│   ├── cycle.py
│   ├── day_type.py
│   ├── metadata.py
│   ├── moment.py
│   ├── planner_configuration.py
│   ├── scheduled_moment.py
│   ├── time_definition.py
│   └── week_schedule.py
└── planner/
    ├── engine.py
    ├── errors.py
    ├── protocols.py
    └── validator.py
```

Tests :

```text
scripts/tests/
├── conftest.py
├── test_config_flow.py
├── test_domain.py
├── test_engine.py
├── test_init.py
├── test_options_flow.py
├── test_services.py
├── test_storage.py
└── test_validator.py
```

## 3. Modèle de domaine

### Moment

```python
@dataclass(frozen=True, slots=True)
class Moment:
    id: str
    name: str
    icon: str
```

### DayType

```python
@dataclass(frozen=True, slots=True)
class DayType:
    id: str
    name: str
    scheduled_moments: tuple[ScheduledMoment, ...]
```

### ScheduledMoment

```python
@dataclass(frozen=True, slots=True)
class ScheduledMoment:
    moment_id: str
    time_definition: TimeDefinition
```

### TimeDefinition

État actuel :

```python
@dataclass(frozen=True, slots=True)
class TimeDefinition:
    fixed_time: time
```

Sérialisation avec `time.isoformat()` et désérialisation avec `time.fromisoformat()`.

À ce stade, `TimeDefinition` ne possède pas de champs `hour` ou `minute`.

### WeekSchedule

Contient les sept associations :

```text
monday
tuesday
wednesday
thursday
friday
saturday
sunday
```

### Cycle

```text
id
name
week_schedule_ids
```

La validation impose :

```text
1 ≤ len(week_schedule_ids) ≤ 4
```

### CalendarException

```text
id
date
day_type_id
description
```

### Action

```python
@dataclass(slots=True)
class Action:
    service: str
    data: dict[str, str]
```

### Audit

```python
@dataclass(slots=True)
class Audit:
    created_by: str
    created_at: datetime
    modified_by: str
    modified_at: datetime
```

## 4. PlannerConfiguration

`PlannerConfiguration` est le conteneur racine du modèle métier :

```text
moments
day_types
week_schedules
cycles
calendar_exceptions
```

Les collections sont actuellement représentées sous forme de tuples.

Une configuration vide est disponible avec :

```python
PlannerConfiguration.empty()
```

## 5. PlannerEngine

`PlannerEngine` constitue le moteur métier principal.

Il fournit actuellement les opérations CRUD pour :

- `Moment`
- `DayType`
- `WeekSchedule`
- `Cycle`
- `CalendarException`

ainsi que la gestion des `ScheduledMoment`.

Exemples :

```python
get_moment()
add_moment()
update_moment()
remove_moment()
```

Avant d'accepter une modification, le moteur soumet la nouvelle configuration au validateur.

## 6. Validation

`PlannerValidator` assure la cohérence globale de `PlannerConfiguration`.

Il vérifie notamment :

- identifiants uniques ;
- références existantes ;
- doublons de moments dans un `DayType` ;
- nombre de `WeekSchedule` dans un `Cycle` ;
- références des `CalendarException`.

Les erreurs de cohérence utilisent `ValidationError`.

Les recherches d'objets inexistants utilisent `NotFoundError`.

## 7. Stockage

`DayPlannerStorage` encapsule le stockage Home Assistant.

Fichier :

```text
/config/.storage/day_planner_configuration
```

Flux :

```text
PlannerConfiguration
       │
       ▼
    to_dict()
       │
       ▼
 Home Assistant Store
       │
       ▼
   async_load()
       │
       ▼
from_dict()
       │
       ▼
PlannerConfiguration
```

Méthodes principales :

```python
async_load()
async_save()
async_delete()
```

## 8. Runtime

`DayPlannerRuntimeData` contient notamment :

```text
storage
engine
```

Chargement :

```text
ConfigEntry
    ↓
DayPlannerStorage
    ↓
configuration
    ↓
PlannerEngine
    ↓
DayPlannerRuntimeData
    ↓
entry.runtime_data
```

## 9. Initialisation

`async_setup_entry()` :

1. crée le stockage ;
2. charge la configuration ;
3. initialise le stockage si aucune donnée n'existe ;
4. crée `PlannerEngine` ;
5. crée `DayPlannerRuntimeData` ;
6. initialise les services ;
7. associe le runtime à la Config Entry.

## 10. Déchargement

`async_unload_entry()` retourne actuellement `True`.

La gestion détaillée du déchargement pourra être enrichie lorsque de nouvelles ressources seront ajoutées.

## 11. Suppression

`async_remove_entry()` examine :

```python
CONF_DELETE_DATA_ON_REMOVE
```

Si l'option est activée :

```python
DayPlannerStorage.async_delete()
```

est appelé.

## 12. Config Flow

Le Config Flow crée une unique configuration Day Planner.

Flux actuel :

```text
async_step_user
      ↓
async_set_unique_id(DOMAIN)
      ↓
_abort_if_unique_id_configured()
      ↓
async_create_entry()
```

Le flow est en version `1` et ne demande actuellement aucun paramètre utilisateur.

## 13. Options Flow

L'Options Flow gère actuellement :

```text
CONF_DELETE_DATA_ON_REMOVE
```

Le flux utilise `async_step_init()` et un schéma `vol.Schema`.

Lors de la validation :

```python
async_create_entry(
    title="",
    data=user_input,
)
```

est appelé.

## 14. Services

Les services récupèrent le runtime avec :

```python
_get_runtime(hass)
```

Flux :

```text
Service
  ↓
_get_runtime()
  ↓
DayPlannerRuntimeData
  ↓
PlannerEngine
  ↓
validation
  ↓
save
```

## 15. Séparation domaine / Home Assistant

Principe à conserver :

```text
                    Day Planner
                         │
              ┌──────────┴──────────┐
              │                     │
          DOMAINE                HOME ASSISTANT
              │                     │
       ┌──────┴──────┐        ┌─────┴─────────┐
       │             │        │               │
    Domain       Planner    Config Flow     Services
    objects       Engine    Options Flow    Storage
                   │         Runtime
                Validator
```

Le domaine ne doit pas dépendre inutilement de Home Assistant.

Cette séparation permet des tests rapides, une logique métier indépendante et une évolution plus simple du moteur.

## 16. Tests

Dernier résultat validé :

```text
97 passed in 0.29s
```

Couverture :

```text
477 statements
0 missed
100%
```

Commande de référence :

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest   -p pytest_asyncio   -p pytest_cov   --cov=custom_components.day_planner   --cov-report=term-missing   scripts/tests -q
```

## 17. État technique de référence

La base actuelle est stable pour poursuivre le développement :

```text
Domaine             100 %
Validator           100 %
Engine              100 %
Storage             100 %
Services            100 %
Config Flow         100 %
Options Flow        100 %
Initialisation      100 %
Couverture globale  100 %
```

Toute nouvelle fonctionnalité doit idéalement être accompagnée de ses tests.

## 18. Évolutions prévues

Les fonctionnalités suivantes restent à développer :

- calcul du planning courant ;
- détermination du type de journée pour une date ;
- déroulement complet d'un cycle ;
- exécution des actions ;
- calendrier interne ;
- calendrier Google ;
- interface complète de gestion des objets ;
- définitions horaires avancées.

Ces évolutions devront conserver la séparation entre domaine, moteur, stockage et intégration Home Assistant.
