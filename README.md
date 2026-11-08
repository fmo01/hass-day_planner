# Day Planner

> **État au 8 novembre 2026.** Base de développement : Day Planner 0.2.3, avec les modifications locales de reprise eedomus **v5.16**. Ces numéros `v5.x` sont ceux des correctifs de travail, pas des versions publiées de l’intégration. Le dernier rapport pytest **complet communiqué** (7 novembre) donne **517 tests réussis, 2 990 instructions, 243 non couvertes, 92 % de couverture**. Un complément de **55 tests** a été préparé et validé de façon ciblée ; **le 100 % global reste à confirmer par la prochaine exécution complète**.


Day Planner est une intégration Home Assistant permettant de définir des moments, des types de journée, des types de semaine et des cycles, puis d'appliquer des exceptions pour certaines dates.

Les horaires sont définis dans les types de journée. Les actions associées aux moments sont exécutées par Home Assistant aux horaires calculés.

## Démarrage

1. Installer les fichiers de l'intégration dans `custom_components/day_planner`, puis redémarrer Home Assistant.
2. Ajouter **Day Planner** depuis **Paramètres → Appareils et services → Ajouter une intégration**.
3. Ouvrir **Day Planner** dans le menu latéral, ou accéder directement à `/day-planner`.
4. Créer les moments et leurs actions, les types de journée avec leurs horaires, les types de semaine, puis un cycle commençant un lundi.
5. Utiliser le calendrier du panneau pour consulter le planning et gérer les exceptions.

Depuis **Configurer**, les paramètres permettent de masquer l'entrée du menu latéral, de choisir le nombre maximal de cycles et de supprimer les données lors du retrait de l'intégration.

## Reprise ponctuelle d’un agenda eedomus (développement v5.16)

L'assistant **Configurer → Reprise agenda eedomus** permet de choisir une **box active**, de sélectionner l'export **JSON directement depuis le navigateur** et de prévisualiser la création des semaines, types de journée, moments, horaires et actions compatibles. L'opération est ponctuelle : aucune synchronisation, aucun cycle ou exception créé automatiquement, aucune action HA exécutée lors de l'import.

Les associations eedomus → Home Assistant s'appuient sur le registre des entités de la box sélectionnée. Les domaines non compatibles (notamment `sensor`) apparaissent comme **ignorés**, sans empêcher la création des moments ; les erreurs de résolution absente ou ambiguë restent bloquantes. Les noms et identifiants Day Planner sont dérivés de `Eedomus (<hôte>)` ; les `unique_id` des entités HA existantes ne sont jamais modifiés.

La confirmation présente un tableau et une zone sélectionnable de copie (Ctrl+A, Ctrl+C), ainsi que des téléchargements **CSV** et **XLSX**. Le classeur comporte **7 onglets**. Les liens sont temporaires ; le comportement du clic dépend aussi de l'interface Home Assistant. L'export est généré en mémoire sans conservation permanente dans `/config`.

**Documentation :** [utilisation et limites](docs/reprise_eedomus.md) ; [structure du classeur Excel](docs/export_xlsx_eedomus.md).

## Validation et couverture

Le dernier résultat **global et reproductible communiqué** avant le complément est de **517 tests réussis, 92 % (2 990 instructions, 243 non couvertes)**. Les tests supplémentaires ont été vérifiés par modules dans un environnement isolé ; ils visent **100 %** sans exclusions ni `--cov-fail-under=100`, mais ce chiffre doit être confirmé sur l'environnement Home Assistant complet.

Commande :

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio -p pytest_cov scripts/tests/ \
  --cov=custom_components/day_planner --cov-report=term-missing -q
```

Voir [la documentation des tests](scripts/tests/README.md) et [le suivi de couverture](docs/qualification_couverture.md).

## Documentation

- [Documentation fonctionnelle](docs/day_planner_fonctionnel.md)
- [Documentation technique](docs/day_planner_technique.md)

- [Reprise eedomus : guide utilisateur et règles fonctionnelles](docs/reprise_eedomus.md)
- [Export XLSX eedomus (7 onglets)](docs/export_xlsx_eedomus.md)
- [État des tests et procédure de validation](docs/qualification_couverture.md)
- [Roadmap et lots de suivi](docs/ROADMAP.md)
