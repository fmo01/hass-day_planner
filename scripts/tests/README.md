# Suite de tests de hass-day_planner

Ce répertoire contient les tests automatisés de l'intégration personnalisée **Day Planner** pour Home Assistant : domaine métier, configuration, calcul du planning, planification, actions, stockage, services, WebSocket, entités et panneau.

Ce document est destiné à `scripts/tests/README.md`. Il conserve la mise à jour automatique des statistiques par le workflow GitHub Actions **Run Tests**.

---

## État actuel des tests

Ce bloc est remplacé automatiquement après une exécution réussie. Les anciens résultats eedomus ont été retirés ; les valeurs Day Planner restent à mesurer.

<!-- TEST-STATS-START -->
- Tests réussis : **à mesurer**
- Instructions mesurées : **à mesurer**
- Instructions couvertes : **à mesurer**
- Instructions non couvertes : **à mesurer**
- Couverture : **à mesurer**
<!-- TEST-STATS-END -->

La dernière exécution réussie mesurant `custom_components/day_planner` et ses rapports font référence.

---

## Organisation des tests

### Cœur de l'intégration

- `test_init.py`
  - Initialisation avec configuration vide ou existante.
  - Création du runtime et nombre maximal de cycles.
  - Rechargement après modification des options.
  - Déchargement réussi ou refusé.
  - Suppression avec conservation ou effacement des données.
  - Migration des identifiants d'entités : entrées présentes, absentes ou déjà migrées.
  - Enregistrement des commandes WebSocket et du répertoire statique du frontend.

- `test_config_flow.py`
  - Création de la configuration depuis le flow utilisateur.
  - Obtention du flow des options.

- `test_options_flow.py`
  - Menus, formulaires, sélection et édition des objets du planning.
  - Ajout, modification et suppression des moments, journées, moments planifiés, semaines, cycles et exceptions.
  - Confirmations de suppression et dépendances empêchant une suppression.
  - Gestion des actions et refus des séquences vides.
  - Paramètres, limites des cycles et conservation des autres options.
  - Lien vers le panneau et retour au menu.

- `test_integration_info.py`
  - Version et attributs d'information de l'intégration.

---

## API et moteur de planification

- `test_websocket_api.py`
  - Enregistrement des commandes et récupération du runtime.
  - Lecture de la configuration et du calendrier.
  - Création, modification et suppression des objets et actions.
  - Dates et heures invalides, limites des cycles et doublons.
  - Erreurs métier, configuration absente et erreurs de mise à jour du runtime.
  - Contexte d'une exception dans le calendrier.

- `test_engine.py`
  - Recherche, ajout, modification et suppression des objets.
  - Moments planifiés et actions des moments.
  - Objets absents, références inconnues et dépendances de suppression.
  - Nombre maximal de cycles.

- `test_resolver.py`
  - Résolution sans cycle ou avant son début.
  - Alternance des semaines et choix du dernier cycle commencé.
  - Priorité des exceptions et contexte du jour.
  - Résolution des moments et mise à jour de la configuration.

- `test_scheduler.py`
  - Événements d'une date et prochain événement.
  - Absence d'événement, événement à l'instant courant et absence de rattrapage.
  - Événement actif et dernier moment atteint dans la journée.
  - Normalisation des dates/heures et fuseau horaire.
  - Replanification après modification de la configuration.

- `test_ha_scheduler.py`
  - Enregistrement du prochain rappel Home Assistant.
  - Exécution puis replanification.
  - Annulation et remplacement du rappel.
  - Fuseau horaire et replanification après erreur.
  - Absence de rattrapage et protection contre l'exécution répétée du même rappel.

- `test_action_executor.py`
  - Exécution d'une action et des actions d'un moment.
  - Moment sans action.
  - Poursuite des actions suivantes après une erreur.

---

## Modèle métier et stockage

- `test_domain.py`
  - Sérialisation et désérialisation des modèles et de la configuration.
  - Moments avec actions, journées, semaines, cycles et exceptions.
  - Horaires fixes, moments planifiés et configuration vide.
  - Libellé d'action par défaut et données historiques sans libellé.
  - Construction de la classe `Audit` ; ce test ne garantit pas une traçabilité intégrée au stockage.

- `test_validator.py`
  - Configurations valides et identifiants en doublon.
  - Références aux moments et doublons dans une journée.
  - Cycles de 1 à 4 semaines et références de semaines inconnues.
  - Début des cycles un lundi, dates uniques et limite du nombre de cycles.
  - Références des exceptions et unicité de leurs dates.
  - Identifiants et séquences des actions.

- `test_storage.py`
  - Chargement vide ou existant, sauvegarde et suppression.
  - Conservation des actions lors de la conversion des données.

- `test_runtime.py`
  - Assemblage des composants du runtime.

La synchronisation `async_configuration_updated()` est également testée dans `test_services.py`.

---

## Plateformes d'entités

- `test_sensor.py`
  - Création des trois capteurs : prochain événement, type de journée et moment courant.
  - Valeurs, attributs et absence d'événement ou de contexte.
  - Actualisation après modification du planning.

- `test_calendar.py`
  - Création du calendrier et événement courant ou prochain.
  - Absence d'événement, liste d'événements et filtrage d'une plage.
  - Actualisation après modification et attributs de l'intégration.

---

## Services et interface de gestion

- `test_services.py`
  - Ajout, modification et suppression des objets du planning.
  - Modification ou effacement des actions d'un moment.
  - Configuration absente, erreurs métier et erreurs inattendues.
  - Sauvegarde, mise à jour du résolveur, replanification et signal de modification.

- `test_panel.py`
  - Enregistrement avec ou sans entrée dans le menu latéral.
  - Retrait du panneau au déchargement.

Les tests Python ne remplacent pas une vérification visuelle du panneau et de la carte Lovelace dans Home Assistant.

---

## Exécution des tests

Exécuter les commandes depuis la racine du projet, avec l'environnement virtuel de développement activé.

### Exécuter toute la suite

```bash
PYTHONPATH=. python3 -m pytest scripts/tests/
```

Pour un affichage détaillé et des traces courtes :

```bash
PYTHONPATH=. python3 -m pytest scripts/tests/ -v --tb=short
```

Pytest découvre les fichiers `test_*.py`. Aucun `test_all.py` n'est présent dans le ZIP de référence ; la découverte automatique est utilisée.

---

## Exécuter un module de tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest   -p pytest_asyncio scripts/tests/test_init.py -v
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest   -p pytest_asyncio scripts/tests/test_engine.py -v
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest   -p pytest_asyncio scripts/tests/test_ha_scheduler.py -v
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest   -p pytest_asyncio scripts/tests/test_config_flow.py -v
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest   -p pytest_asyncio scripts/tests/test_options_flow.py -v
```

---

## Exécuter un test individuel

```bash

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio \
  scripts/tests/test_ha_scheduler.py::test_ha_scheduler_does_not_execute_same_callback_twice \
  -v
```

---

## Couverture du code

Le workflow **Run Tests** calcule la couverture, produit les rapports et actualise ce README après une exécution réussie.

Commande à utiliser pour Day Planner, également exécutable localement :

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio \
  -p pytest_cov \
  scripts/tests/ \
  -v \
  --tb=short \
  --junitxml=pytest-results.xml \
  --cov=custom_components/day_planner \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-report=html
```

Les fichiers produits sont :

- `pytest-results.xml` : résultats JUnit pour le décompte des tests.
- `coverage.xml` : couverture globale et par module.
- `htmlcov/` : rapport HTML détaillé.
- `coverage-summary.md` : synthèse générée par le workflow.

Les artefacts publiés sont `coverage-html` (14 jours) et `coverage-summary` (30 jours).

### Rapport HTML dans GitHub Actions

Télécharger `coverage-html` depuis la dernière exécution réussie, extraire l'archive et ouvrir `index.html`. Selon l'organisation de l'archive, le fichier peut être directement à sa racine.

Le rapport montre les lignes couvertes et non couvertes de chaque fichier source.

### Synthèse de couverture

Télécharger `coverage-summary` et consulter `coverage-summary.md`.

### Rapport HTML local

Après une exécution locale avec couverture, ouvrir :

```text
htmlcov/index.html
```

### Résultat de référence

Les résultats Day Planner du workflow et les blocs automatiques ci-dessous font référence.

---

## Couverture par module

 Les valeurs ci-dessous proviennent de l'exécution locale réussie et ne sauraurent être considérées comme définitivement à jour.

<!-- COVERAGE-MODULES-START -->
Dernière mise à jour : **en attente d'une exécution Day Planner**

| Composant | Instructions | Non couvertes | Couverture |
| --- | ---: | ---: | ---: |
| **TOTAL** | **à mesurer** | **à mesurer** | **à mesurer** |
<!-- COVERAGE-MODULES-END -->

---

## GitHub Actions

Le workflow fourni conserve ce fonctionnement :

1. Push et pull requests ciblant `main` ou `unstable`, pour les chemins surveillés, ou lancement manuel.
2. Installation de Python 3.14 et des dépendances de développement.
3. Exécution de pytest avec couverture et rapport JUnit.
4. Génération de la synthèse après succès.
5. Remplacement des trois blocs automatiques du README.
6. Commit et push du README modifié après un événement `push` réussi. Aucun commit automatique pour une pull request ou un lancement manuel.
7. Publication du rapport HTML même après échec, s'il existe, et de la synthèse après succès.

La commande pytest ne masque plus les erreurs : un échec fait échouer l'étape de tests.

---

## Stratégie de tests

La suite utilise pytest, les tests asynchrones et des doublures adaptées aux composants testés, notamment `MagicMock` et `AsyncMock`. `pytest-cov` mesure la couverture. Les fixtures Home Assistant peuvent être utilisées lorsque le niveau du test l'exige.

Les tests ne doivent pas agir sur des appareils réels ni dépendre d'un calendrier externe. Les rappels temporels, appels de services, écritures de stockage et ressources Home Assistant sont isolés selon les scénarios.

Les commandes documentées conservent le chargement automatique des plugins pytest de l'environnement actif.

La couverture ne garantit pas à elle seule la correction des règles métier. Vérifier les résultats attendus, limites et erreurs, puis compléter par les essais Home Assistant nécessaires.

---

## Dépendances de développement

```bash
python3 -m pip install -r requirements-dev.txt
```

Le workflow fourni utilise aussi `pytest-cov` pour les rapports et lit la version de `pytest-homeassistant-custom-component` pour le bloc d'environnement.

---

## Ajouter de nouveaux tests

1. Compléter de préférence le fichier de tests existant correspondant au module modifié.
2. Vérifier les comportements attendus et les chemins d'erreur pertinents.
3. Isoler les dépendances externes et les effets réels sur Home Assistant.
4. Utiliser les fixtures adaptées au niveau du test.
5. Exécuter le module concerné puis toute la suite.
6. Contrôler la couverture du code modifié, avec l'objectif de 100 % du code Python mesuré.
7. Consulter les rapports GitHub Actions après l'exécution.

Les nouveaux fichiers `test_*.py` sont découverts automatiquement ; aucun ajout à un lanceur `test_all.py` n'est requis.

---

## Périmètres actuellement testés

- Initialisation et cycle de vie de l'intégration.
- Config Flow et Options Flow.
- Modèles métier et sérialisation.
- Moteur et dépendances de suppression.
- Validation du planning.
- Résolution des cycles, semaines, journées et exceptions.
- Calcul des événements et du moment courant.
- Planification Home Assistant, annulation et replanification.
- Exécution des actions et poursuite après erreur.
- Stockage et runtime.
- Services et WebSocket.
- Capteurs et calendrier.
- Enregistrement et retrait du panneau.
- Informations de version.
- Scénarios d'erreur et de configuration absente.

Cette liste décrit les tests présents ; elle ne garantit pas une couverture exhaustive de toutes les règles.

---

## État de l'environnement de test

L'exécution locale récente réussie a utilisé:

<!-- TEST-ENV-START -->
```text
Python : à renseigner automatiquement
pytest : à renseigner automatiquement
pytest-cov : à renseigner automatiquement
pytest-homeassistant-custom-component : à renseigner automatiquement
Tests exécutés : à mesurer
Tests réussis : à mesurer
Couverture totale : à mesurer
Dernière exécution : en attente d'une exécution Day Planner
```
<!-- TEST-ENV-END -->

Les versions GitHub Actions peuvent différer de l'environnement local. La dernière exécution réussie ciblant Day Planner et ses rapports font référence.
