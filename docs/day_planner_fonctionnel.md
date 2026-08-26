# Day Planner — Documentation fonctionnelle

**Version de référence : 0.0.x**

## 1. Présentation

Day Planner est une intégration Home Assistant destinée à gérer un planning journalier et hebdomadaire.

Elle permet de définir des **moments**, des **types de journée**, des horaires associés aux moments, des **types de semaine**, des **cycles** de semaines et des **exceptions de calendrier**.

Le planificateur détermine quand un moment doit se produire. Les actions exécutées à ce moment constituent une couche fonctionnelle complémentaire.

## 2. Concepts

### Moment

Un moment représente un événement logique de la journée.

Exemples : Réveil, Départ, Retour, Coucher, Nuit.

Un moment possède :
- `id`
- `name`
- `icon`

Le moment ne définit pas son heure.

### Type de journée

Un type de journée représente une journée particulière : Travail, Télétravail, Week-end, Vacances, Garde, Absence, etc.

Il contient une liste de moments planifiés.

Exemple :

```text
Télétravail
08:00  Réveil
09:00  Début travail
12:00  Déjeuner
18:00  Fin travail
23:00  Coucher
```

Le même moment peut avoir une heure différente selon le type de journée.

### Moment planifié

`ScheduledMoment` associe un moment à une définition d'heure :

```text
moment
+
TimeDefinition
```

La définition actuelle utilise une heure fixe :

```text
TimeDefinition
└── fixed_time
```

### Type de semaine

Un `WeekSchedule` associe chacun des sept jours à un type de journée :

```text
Lundi      → Travail
Mardi      → Travail
Mercredi   → Travail
Jeudi      → Travail
Vendredi   → Travail
Samedi     → Week-end
Dimanche   → Week-end
```

### Cycle

Un cycle permet d'enchaîner plusieurs types de semaine.

Exemple :

```text
Cycle garde alternée
Semaine A
Semaine B
```

Le modèle actuel autorise de 1 à 4 types de semaine.

### Exception de calendrier

Une exception remplace le type de journée normalement prévu pour une date donnée.

Exemple :

```text
01/01/2027 → Jour férié
```

Elle contient :
- `id`
- `date`
- `day_type_id`
- `description`

### Actions

Le domaine contient `Action`, représentant un service Home Assistant et ses données.

Exemple conceptuel :

```yaml
service: light.turn_on
data:
  entity_id: light.salon
```

L'exécution complète des actions n'est pas encore considérée comme opérationnelle dans le moteur actuel.

## 3. Règles de cohérence

- Les identifiants doivent être uniques.
- Un `ScheduledMoment` doit référencer un moment existant.
- Un même moment ne peut pas être utilisé deux fois dans un même type de journée.
- Les types de journée référencés doivent exister.
- Les types de semaine référencés doivent exister.
- Un cycle contient de 1 à 4 types de semaine.
- Le type de journée d'une exception doit exister.
- La suppression d'un objet encore utilisé par un autre objet est refusée.

Exemple de dépendances :

```text
Moment
  ↓
DayType
  ↓
WeekSchedule
  ↓
Cycle
```

## 4. Configuration Home Assistant

Day Planner utilise une Config Entry Home Assistant.

La configuration initiale est réalisée via le Config Flow et les paramètres optionnels via l'Options Flow.

L'intégration est conçue pour être configurée depuis l'interface Home Assistant.

## 5. Suppression

L'option `CONF_DELETE_DATA_ON_REMOVE` détermine si les données persistantes doivent être supprimées lors de la suppression de la Config Entry.

## 6. Limites actuelles

Ne sont pas encore considérés comme complètement implémentés :

- détermination complète du jour courant à partir d'un cycle ;
- moteur complet d'exécution des `Action` ;
- calendrier interne complet ;
- intégration Google Calendar ;
- interface utilisateur complète de gestion des objets ;
- définitions horaires autres que `fixed_time`.

## 7. État de validation

La suite actuelle comprend **97 tests** avec **100 % de couverture** du code mesuré.
