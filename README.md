# Day Planner

Day Planner est une intégration Home Assistant permettant de définir des moments, des types de journée, des types de semaine et des cycles, puis d'appliquer des exceptions pour certaines dates.

Les horaires sont définis dans les types de journée. Les actions associées aux moments sont exécutées par Home Assistant aux horaires calculés.

## Démarrage

1. Installer les fichiers de l'intégration dans `custom_components/day_planner`, puis redémarrer Home Assistant.
2. Ajouter **Day Planner** depuis **Paramètres → Appareils et services → Ajouter une intégration**.
3. Ouvrir **Day Planner** dans le menu latéral, ou accéder directement à `/day-planner`.
4. Créer les moments et leurs actions, les types de journée avec leurs horaires, les types de semaine, puis un cycle commençant un lundi.
5. Utiliser le calendrier du panneau pour consulter le planning et gérer les exceptions.

Depuis **Configurer**, les paramètres permettent de masquer l'entrée du menu latéral, de choisir le nombre maximal de cycles et de supprimer les données lors du retrait de l'intégration.

## Documentation

- [Documentation fonctionnelle](docs/day_planner_fonctionnel.md)
- [Documentation technique](docs/day_planner_technique.md)
