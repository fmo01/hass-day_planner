# Day Planner — Qualification et couverture Python

**Mise à jour documentaire : 8 novembre 2026.** Périmètre : v5.16 de la reprise eedomus et suite de tests Day Planner, sans nouvelle publication ni modification de code métier.

## Dernier rapport complet fourni par l’utilisateur

| Mesure | Valeur (7 novembre 2026) |
| --- | ---: |
| Tests réussis | **517** |
| Avertissements | **5** (dépréciations Home Assistant/backoff) |
| Instructions mesurées | **2 990** |
| Instructions non couvertes | **243** |
| Couverture globale | **92 %** |

Lignes restantes : `eedomus_agenda_extract.py` **202** ; `eedomus_import.py` **15** ; `eedomus_excel.py` **1** ; `options_flow.py` **25**. Tous les autres modules du dernier rapport étaient à 100 %.

## Complément de tests préparé

**55 nouveaux tests**, quatre fichiers concernés : `test_eedomus_agenda_extract.py` (nouveau, 40 scénarios), `test_eedomus_import.py`, `test_eedomus_excel.py` et `test_options_flow.py`. Pas de modification du code applicatif. Vérifications ciblées effectuées (90 tests sélectionnés passés dans un environnement isolé). Les modules extracteur, importeur et Excel ont atteint 100 % **isolément** ; les branches d'Options Flow précédemment manquantes ont été testées.

**Statut : objectif 572 tests / 100 % à confirmer par la suite complète.** Aucun résultat ultérieur de `pytest --cov` n'a été fourni ; ne pas publier 100 % comme une mesure acquise. Les 449 tests / 100 % de la version antérieure constituent un jalon historique et non le résultat du nouveau périmètre.

## Reproduire la mesure

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_asyncio -p pytest_cov scripts/tests/ \
  --cov=custom_components/day_planner --cov-report=term-missing -q
```

Ne pas ajouter `--cov-fail-under=100`, de règle `omit` ni de `# pragma: no cover` pour gonfler la mesure. Vérifier Black, `isort --profile black`, flake8 ainsi que les essais HA OS des formulaires et téléchargements.

Après validation, actualiser **L6-10** de la roadmap, puis laisser le workflow GitHub Actions mettre à jour les blocs automatiques `TEST-STATS`, `COVERAGE-MODULES` et `TEST-ENV` de `scripts/tests/README.md`.
