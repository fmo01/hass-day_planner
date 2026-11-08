# Day Planner — Roadmap et suivi d’avancement

**Actualisation du 8 novembre 2026 :** revue documentaire de la reprise eedomus **v5.16** et ajout du suivi de couverture **L6-10**. Le dernier rapport de suite complète communiqué fait état de **517 tests réussis, 2 990 instructions mesurées, 243 non couvertes, soit 92 %** (Python 3.14.3, 5 avertissements). Un complément de 55 tests a été préparé ; des tests ciblés sont réussis, mais le retour à **100 % en suite complète n’est pas encore attesté par un nouveau rapport utilisateur**. Les résultats historiques à 100 % concernent le périmètre antérieur. Le lot 7 reste reporté à très long terme ; le classeur v5.16 conserve ses sept onglets.


**Actualisation du 7 novembre 2026 : ajout du lot 7 — évolutions futures du classeur XLSX de reprise eedomus.** Les six lots initiaux, leurs identifiants et leur historique sont conservés. Le classeur v5.16 à sept onglets reste inchangé pour l’instant. Priorité très basse et aucune échéance fixée.

**Mise à jour : 29 octobre 2026. ZIP source actuel fourni : 0.2.3 (manifest.json). Dernière publication explicitement confirmée dans le suivi historique : 0.2.0. Traçabilité `Audit` intégrée ; L1-06 (sept essais réels) et L1-11 (absence de rattrapage après arrêt) clôturés. L3-06 et L3-07 validés, et L3-08 qualifié : cache frontend OK, accès complet des non-administrateurs constaté, gestion fine des droits reportée (L3-12). L3-10 est maintenant terminé : duplications des Moments, Actions, Types de journée, Semaines types, Cycles et Exceptions validées dans Home Assistant au 28/10. Sur décision utilisateur du 27/10, « Dupliquer » est retiré des Moments planifiés (timeline) ; Ajouter/Modifier/Supprimer restent disponibles. L6-03 clôturé le 29/10 : contrôles syntaxiques, essais frontend et validations en HA (tri, compteurs, erreurs, i18n FR/EN et infobulles au survol). L6-04 clôturé le 29/10 : Black, isort (profil black), flake8 validés localement, 449 tests Python réussis et 100 % de couverture (2 154 instructions, aucune non couverte), et quatre workflows GitHub Actions confirmés OK par l’utilisateur (Lint & Formatting, HACS Validate, Validate with hassfest, Run Tests). L6-07 — installation, mise à jour et retrait — est en cours : installation neuve **validée le 29/10 sur HAOS de test** (tous les résultats attendus OK), scénario de mise à jour 0.2.2 vers le code courant préparé ; retrait à traiter ensuite. Il ne s’agit pas d’une nouvelle publication.**

La roadmap conserve les **six lots de la première version** et ajoute un **lot 7 distinct, reporté à très long terme**, pour l’export XLSX eedomus. Les sept étapes de finalisation des vues sont rattachées aux lots concernés, avec leurs statuts conservés. Les numéros des lots sont des repères stables ; les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. Les sept essais fonctionnels prévus pour L1-06 sont validés le 22 octobre ; L3-06 est clôturé le 23 octobre après validation des contrôles d’erreurs et d’annulation ; L3-07 est clôturé le 24 octobre après les validations sur ordinateur et mobile. L3-08 a été qualifié le 24 octobre : chargement des fichiers frontend avec rechargement simple après mise à jour/redémarrage et droits CRUD des non-administrateurs constatés. La délégation fine des droits reste volontairement reportée à L3-12. L1-11 a été validé en conditions réelles le 26 octobre ; L3-10 est terminé le 28 octobre : Moments validés le 27 octobre (Enregistrer et Annuler) ; Actions validées en HA pour les essais 4 et 5 ; Types de journée, Semaines types, Cycles et Exceptions validés. Duplication des Moments planifiés retirée le 27 octobre (la création standard reste disponible). Les essais HA n’impliquent pas une nouvelle exécution complète des tests Python. L6-03 est validé le 29 octobre : 12 fichiers JS et 2 JSON syntaxiquement valides, contrôle de navigation, amélioration Types de journée (tri, compteurs, dépendances, i18n FR/EN), puis affichage des détails au survol validé.

Les statuts des vues proviennent des essais HA confirmés par l’utilisateur jusqu’au 19 octobre. Les constats techniques combinent la relecture historique du ZIP et celle des 14 fichiers frontend actualisés, puis du dernier day-planner-card.js du 19 octobre. La vérification finale des six corrections est une relecture du code et un contrôle syntaxique ; les simulations de doubles appels ont été effectuées sur la version précédente. Les versions cibles restent indicatives, sans date de publication engagée.

## 1. Principes

- Un seul profil et une seule configuration Day Planner.
- Horaires définis dans les types de journée ; actions associées aux moments.
- Exceptions gérées depuis le calendrier.
- Logique métier séparée des interfaces Home Assistant.
- Nouveaux tests ajoutés de préférence dans les fichiers existants correspondant aux modules concernés.
- Moments considérés comme terminés et figés : une modification nécessite un défaut identifié ou une dépendance concrète d'un autre bloc.
- Couverture mesurée et suivie, avec un objectif de 100 %, sans seuil bloquant dans les commandes ni dans la CI.

### Priorité de l'i18n

**L'i18n n'est pas prioritaire et ne bloque pas la validation des blocs.** Lorsqu'un fichier ou un dialogue doit être retouché pour une raison fonctionnelle, son i18n peut être traitée à cette occasion. Les traductions existantes sont conservées.

Les mentions d'i18n dans les blocs suivants décrivent donc des ajustements opportunistes, pas une campagne de traduction dédiée. Les libellés encore en français en dur seront recensés lors du passage transversal ; leur traduction n'impose pas de rouvrir les moments figés.

## 2. État du socle

### Présent dans la version relue

- Gestion des moments, actions, types de journée, moments planifiés, semaines types, cycles et exceptions.
- Résolution du planning, calcul des événements, planification Home Assistant et exécution des actions.
- Stockage persistant, trois capteurs et un calendrier Home Assistant.
- Panneau de gestion, carte Lovelace, services et API WebSocket.
- Horaires fixes.

### Corrections intégrées depuis la première relecture

- Couverture ciblant `custom_components/day_planner`.
- Suppression des anciennes vérifications de fichiers eedomus dans le workflow de tests.
- Échec de pytest désormais transmis à la CI.
- Dépendances de test et de couverture ajoutées.
- Assertions des capteurs et du calendrier utilisant `INTEGRATION_VERSION`.
- Tableau de couverture distinguant package et composant.
- README des tests en français, guides et roadmap intégrés au dépôt.

**Rapport historique complet chiffré communiqué par l’utilisateur le 29 octobre 2026 : 449 tests réussis, 2 154 instructions mesurées, 0 non couverte, 100 % de couverture Python, 5 avertissements, 2,26 s, Python 3.14.3.** Ce nouveau résultat suit la mise en forme Black/isort et les vérifications flake8. **Résultat historique du 21 octobre 2026 conservé :** 449 tests, 2 146 instructions mesurées, 0 non couverte, 100 %, 5 avertissements, 1,67 s. Le 20 octobre, le retour à 100 % après compléments `action_executor.py` et `logbook.py` avait déjà été confirmé. **Résultat historique du 14 octobre :** 407 tests réussis, 1 908 instructions mesurées, aucune non couverte, 100 % de couverture Python, 5 avertissements, 1,22 s, Python 3.14.3. Ces résultats ne sont pas des exécutions de la suite complète par l'assistant. Aucun seuil bloquant de couverture n'est souhaité.

**Résultat historique du 13 octobre :** le README des tests annonce **394 tests réussis, 1 877 lignes mesurées et 100 % de couverture**, au **13 octobre 2026 à 15:28:05 Europe/Paris**. La relecture a vérifié la cohérence de ce tableau et les générateurs de rapports avec des données synthétiques ; elle n'a pas réexécuté la suite complète.

### Référence du développement eedomus v5.16 (hors releases historiques)

Reprise ponctuelle par `options_flow`, téléversement JSON par le navigateur, choix des seules box eedomus actives, associations avec ou sans préfixe `eedomus_` et avec ou sans suffixe, exclusion `_battery`. Les entités non acceptées (`sensor`, etc.) sont **signalées mais non intégrées comme actions** ; un moment sans action reste créé. Noms et identifiants des objets Day Planner fondés sur `Eedomus (<api_host>)` ; les `unique_id` des entités eedomus de HA restent inchangés. Prévisualisation, confirmation de remplacement, copie et export XLSX à **sept onglets**. Pas de cycle ni d'exception automatiquement créés.

**Statut de recette :** fonctionnalités testées en partie sur HA par l’utilisateur au fil des correctifs, sans rapport de validation globale de la v5.16 accompagné du complément de tests. Maintenir les règles et les limites détaillées dans `docs/reprise_eedomus.md` et `docs/qualification_couverture.md`.

## 3. Vue d’ensemble des lots

| Lot | Intitulé | Version cible indicative | Avancement actuel |
| --- | --- | --- | --- |
| 1 | Stabiliser le socle | Corrections livrées en 0.2.0 | Corrections fonctionnelles, workflow et versions/changelog terminés ; L1-06 validé le 22/10 et L1-11 validé le 26/10 après arrêt couvrant un événement. |
| 2 | Intégrer les Metadata / `Audit` | À définir après 0.2.0 | Modèles, moteur, persistance et trois interfaces validés ; présentation détaillée des métadonnées dans l’interface restant à qualifier. |
| 3 | Simplifier la gestion quotidienne | 0.3.0 | En cours ; les cinq vues sont validées. Formulaires (L3-06), clavier/mobile (L3-07) validés ; L3-08 qualifié (cache OK, permissions existantes constatées). Attribution fine des droits reportée (L3-12). Duplication (L3-10) terminée le 28/10 : six familles validées en HA ; bouton Dupliquer des Moments planifiés retiré sur décision du 27/10. L6-03 validé le 29/10 ; L6-04 validé le 29/10 (lint, HACS, hassfest et tests CI). Prochaine priorité : L6-07 (installation / mise à jour / retrait). |
| 4 | Ajouter les horaires avancés | 0.4.0 | À planifier ; périmètre à préciser. |
| 5 | Ajouter une source de calendrier externe | 0.5.0 | À planifier ; règles de synchronisation à définir. |
| 6 | Qualifier la première version stable | 1.0.0 | À préparer après consolidation du périmètre retenu. |
| 7 | Enrichir les propriétés du classeur XLSX de reprise eedomus | Après v5.16, sans version cible | **Reporté — très long terme.** Conserver les sept onglets actuels ; priorité à l’enrichissement des propriétés du fichier lui-même, révision des onglets uniquement si nécessaire. |

Les lots 4 et 5 peuvent être inversés selon les besoins. La 1.0 peut être qualifiée avec calendrier interne et horaires fixes, sans attendre ces extensions.

## 4. Tableau permanent de suivi d’avancement

**Ce tableau est conservé et mis à jour au fil du projet, sans suppression de lignes.** Les identifiants sont stables et ne sont jamais réutilisés. Une tâche terminée reste visible. Les nouvelles tâches sont ajoutées avec un nouvel identifiant.

Les colonnes statut, reste à faire, preuve et date peuvent être actualisées. Une tâche abandonnée passe à « Abandonné », une tâche reportée à « Reporté » ; la raison est conservée. Un changement de périmètre est consigné dans le journal en fin de document. Aucun pourcentage n'est déduit des lignes : les tâches n'ont pas toutes la même taille.

Statuts : **Terminé**, **Terminé et figé**, **Presque terminé**, **En cours**, **À faire**, **À planifier**, **À confirmer**, **Reporté**, **Abandonné**. « Terminé » décrit une tâche précise ; il ne signifie pas que tout le lot est validé.

| ID | Lot | Tâche / périmètre | Statut | Reste à faire / prochaine action | Preuve / origine du statut | Mise à jour |
| --- | --- | --- | --- | --- | --- | --- |
| L1-01 | 1 | Ciblage Day Planner et transmission des échecs pytest | Terminé | Conserver lors des prochaines adaptations. | Workflow relu. | 13/10/2026 |
| L1-02 | 1 | Dépendances de tests et couverture | Terminé | Suivre leur compatibilité. | requirements-dev.txt relu. | 13/10/2026 |
| L1-03 | 1 | Assertions de version et tableau par package | Terminé | Conserver la génération automatique. | Tests relus ; générateurs vérifiés avec XML synthétiques. | 13/10/2026 |
| L1-04 | 1 | Références des sept jours des semaines types | Terminé | Maintenir les contrôles et tests des sept jours ; L3-03 est maintenant clôturé. | Validation métier du 14/10 ; essais HA des semaines types confirmés par l’utilisateur. | 19/10/2026 |
| L1-05 | 1 | Moments simultanés | Terminé | Maintenir les tests de non-régression dans les fichiers existants. | Deux nouveaux tests réussis ; 29 tests des planificateurs passés, puis suite complète de 403 tests réussie, selon les résultats utilisateur. | 14/10/2026 |
| L1-06 | 1 | Transitions temporelles et rechargement | Terminé | Conserver les validations et tests de non-régression. L’essai distinct après arrêt est validé dans L1-11. | 22/10, sept scénarios HA confirmés successivement par l’utilisateur : action sur deux helpers (logs et événements), deux moments distincts simultanés, modification d’horaire, exception de calendrier, changement de cycle, passage à minuit et redémarrage avant déclenchement. Contrôles Python minuit/DST antérieurs conservés. | 22/10/2026 |
| L1-07 | 1 | Filtres et présentation du workflow | Terminé | Conserver les rapports et la mise à jour automatique du README, sans seuil bloquant. | Exécution tests.yml réussie confirmée par l'utilisateur ; README généré le 14/10 à 12:15:34 : 407 tests, 1 908 instructions, 100 %. | 14/10/2026 |
| L1-08 | 1 | Seuil de couverture imposé en CI | Abandonné | Ne pas ajouter de seuil bloquant ; conserver la mesure et les rapports de couverture. | Décision explicite de l'utilisateur le 14/10 : refus de --cov-fail-under=100. L'objectif de couverture reste suivi. | 14/10/2026 |
| L1-09 | 1 | Versions et changelog | Terminé | Maintenir le manifeste comme référence ; laisser semantic-release gérer les prochaines versions. | Utilisateur : L1-09 terminé. Manifeste 0.2.0 ; ancienne constante supprimée ; entrée 0.1.0 du 10/10 restaurée d'après le tag et doublons retirés. | 14/10/2026 |
| L1-10 | 1 | Journalisation et attribution des actions Day Planner | Terminé (fonctionnement validé) | Conserver les tests de non-régression et contrôler les cas d’intégrations tierces à exécution différée. | 20/10 : deux activités Logbook observées ; `input_boolean.day_planner_test` désactivé avec cause « Day Planner — action XX1 test (id : XX1) ». Journaux DEBUG/INFO/WARNING/ERROR, cibles manquantes et contexte commun couverts par les tests. | 20/10/2026 |
| L1-11 | 1 | Non-rattrapage après arrêt couvrant un événement | Terminé | Maintenir ce comportement et les tests de non-régression. | Test HA réel confirmé le 26/10/2026 : arrêt avant un événement, redémarrage après l’horaire, aucune exécution rétroactive ; reprise de la programmation future. Distinct du redémarrage avant événement validé sous L1-06. | 26/10/2026 |
| L2-01 | 2 | Modèle Metadata et règles auteur/horodatage | Terminé | Conserver le modèle `Audit` et ses règles ; aucune substitution de classe requise. | 21–22/10 : `Audit` intégré aux cinq objets, dates UTC/ISO, création et modification centralisées dans `PlannerEngine`, anciens objets acceptés sans migration ; tests utilisateur confirmés. | 22/10/2026 |
| L2-02 | 2 | Persistance, migration et interfaces Metadata | En cours | Persistance et trois interfaces validées ; qualifier l’affichage explicite de l’audit dans le panneau / les options. **Aucune migration des anciennes données n’est prévue** dans ce chantier. | 21–22/10 : sérialisation conditionnelle et mutations WebSocket, Services et Options Flow adaptées ; tests Python et essais HA validés. | 22/10/2026 |
| L2-03 | 2 | Validation fonctionnelle de la traçabilité des cinq objets | Terminé | Maintenir les tests et contrôles après modification du moteur ou du frontend. | 22/10 : utilisateur confirme successivement Moments/Actions, Types de journée/Moments planifiés, Semaines types, Cycles et Exceptions ; champs d’audit vérifiés après création et modification. | 22/10/2026 |
| L3-01 | 3 | Moments | Terminé et figé | Maintenir les tests de non-régression. | Statut utilisateur : CRUD, groupes d'actions, détails, traduction HA, i18n, comptages, erreurs. | 13/10/2026 |
| L3-02 | 3 | Types de journée | Terminé | Maintenir les comportements validés ; aucun nouveau travail fonctionnel prévu sur cette vue. | Essais utilisateur HA : CRUD, dépendances et conservation des saisies de création, renommage et moments planifiés. Boutons et gardes relus. | 19/10/2026 |
| L3-03 | 3 | Semaines types | Terminé | Maintenir les sept affectations, la conservation des saisies et les messages dans les dialogues. | Quatre essais HA confirmés : création invalide, modification invalide, CRUD et suppression refusée si utilisée par un cycle ; visibilité des erreurs validée. | 19/10/2026 |
| L3-04 | 3 | Cycles | Terminé | Maintenir le CRUD, les brouillons, les messages i18n et les protections relues ; comportement temporel réel suivi dans L1-06. | Essais HA des cycles tous confirmés le 18/10 ; corrections complémentaires de robustesse relues le 19/10 dans le dernier fichier syntaxiquement valide. | 19/10/2026 |
| L3-05 | 3 | Calendrier / Exceptions | Terminé | Maintenir le remplacement du programme par une exception et le retour au cycle après suppression ; L1-06 reste distinct. | Tous les essais HA confirmés le 19/10 : CRUD, description facultative vide, conservation des saisies, type appliqué et retour au programme après suppression. | 19/10/2026 |
| L3-06 | 3 | Cohérence transversale des modales et messages | Terminé | Maintenir les contrôles de non-régression ; toute nouvelle fenêtre doit respecter les comportements validés. Aucun contrôle de fermeture par croix : les fenêtres testées ne disposent pas de croix. | 22–23/10 : utilisateur confirme message explicite au dépassement de la limite des cycles, conservation des saisies après erreur, correction puis enregistrement, annulation sans mutation et absence de croix. Corrections JS relues le 19/10 ; aucun test supplémentaire inventé. | 23/10/2026 |
| L3-07 | 3 | Nettoyage CSS/JS, accessibilité et responsive | Terminé (contrôles convenus) | Maintenir la navigation au clavier et le rendu mobile lors des évolutions ; les travaux généraux de rationalisation CSS/JS, si nécessaires, restent transversaux et ne rouvrent pas la validation acquise. | 23/10 : après les correctifs L3-07 v2/v3, utilisateur confirme le retour des clics et saisies, le focus initial dans le premier champ, la navigation clavier correcte et la gestion du fond. 24/10 : essai réel sur mobile validé et fermeture par Échap confirmée. Fonctionnement constaté dans HA ; aucune nouvelle exécution complète des tests automatisés n’est impliquée. | 24/10/2026 |
| L3-08 | 3 | Cache/versioning frontend et permissions actuelles | Terminé (contrôles convenus) | Maintenir le comportement constaté jusqu’à la définition des droits fins en L3-12. | 24/10 : après mise à jour et redémarrage, simple rechargement suffisant (pas de Ctrl+Maj+R) ; compte non-administrateur testé : consultation, ajout, modification et suppression possibles. | 24/10/2026 |
| L3-09 | 3 | i18n restante | Reporté | Traiter opportunément lorsqu'un composant est retouché ; ne bloque pas un lot. | Priorité utilisateur. | 13/10/2026 |
| L3-10 | 3 | Dupliquer les six familles retenues en complément de modifier/supprimer (Moments planifiés exclus sur décision) | **Terminé** | Maintenir les six duplications validées et les comportements Annuler/erreurs ; non-régression frontend à poursuivre sous L6-03 et vérification des droits/audits selon les règles existantes. | 27/10 : **duplication d’un Moment validée dans HA, y compris Enregistrer et Annuler**. 27/10 : **duplication d’une Action confirmée en HA** : test 4 Enregistrer OK, test 5 Annuler OK. 27/10 : **Types de journée confirmés dans HA (tous les essais convenus OK)** : copie des affectations et horaires, annulation. **Moments planifiés : décision utilisateur du 27/10, bouton Dupliquer retiré de la timeline et de la fenêtre d’édition.** Le test dans HA a confirmé que le bouton ouvrait un simple formulaire d’ajout d’un autre Moment, peu pertinent comme duplication ; annulation complète du patch de cette fonctionnalité. Ajouter/Modifier/Supprimer restent disponibles. 28/10 : **Semaines types validées dans HA (tous les essais demandés OK)** ; duplication des Cycles validée en HA (test OK signalé par l’utilisateur). 28/10 : duplication des Exceptions validée en HA (tous les tests convenus OK), après les Cycles. Les six familles retenues sont donc validées ; aucune nouvelle exécution Python ni publication n’est déduite de ces essais. | 28/10/2026 |
| L3-11 | 3 | Ajout guidé des moments prédéfinis | À planifier | Conserver comme amélioration future indépendante de L3-10 ; en préciser le parcours après consolidation. | Sous-sujet préexistant à L3-10, conservé lors de sa scission le 22/10/2026. | 22/10/2026 |
| L3-12 | 3 | Gestion déléguée des droits (gestionnaires/lecteurs) | Reporté | Réexaminer après finalisation des autres fonctionnalités : délégation par utilisateur, droit de modifier les actions HA, protection API/WebSocket et services. | Étude d’impact du 24/10, décision utilisateur le même jour de reporter l’évolution sans changer les droits actuels. | 24/10/2026 |
| L4-01 | 4 | Horaires avancés | À planifier | Définir règles, indisponibilités, passages de date et compatibilité. | Évolution conservée. | 13/10/2026 |
| L5-01 | 5 | Source de calendrier externe | À planifier | Définir source, correspondances, priorités et synchronisation. | Évolution conservée. | 13/10/2026 |
| L6-01 | 6 | Résultat de couverture de référence | Terminé | Actualiser après chaque exécution pertinente ; conserver les résultats précédents dans l’historique. | **29/10 : 449 tests, 2 154 instructions, 0 non couverte, 100 %, 5 avertissements, 2,26 s, Python 3.14.3** après formatage. Résultats historiques 21/10 (449 tests, 2 146 instructions, 100 %) et 14/10 conservés. | 29/10/2026 |
| L6-02 | 6 | Validation backend et WebSocket/API après corrections | Terminé | Relancer après de nouvelles modifications ; L1-06 validé le 22/10 et L1-11 validé séparément le 26/10. | **29/10 : suite complète relancée après formatage, 449 tests réussis et couverture 100 %**, selon rapport utilisateur. Résultat historique de 407 tests du 14/10 conservé. | 29/10/2026 |
| L6-03 | 6 | Tests ciblés frontend et essais visuels | **Terminé (contrôles convenus)** | Maintenir les régressions testées et réexaminer si de nouvelles modifications frontend interviennent. Ne pas assimiler les essais HA à une exécution complète des tests Python. | 28/10 : 12 JS et 2 JSON vérifiés sans erreur ; navigation des cinq vues et refus de suppression métier constatés. 28–29/10 : correctif Types de journée sur ZIP 0.2.3, tri « Ajouter un Moment » validé, compteurs présents, suppression et informations de dépendance vérifiées, traductions FR/EN confirmées. 29/10 : infobulles au survol et fermeture automatique validées par l’utilisateur (« test ok »). Version JS de référence après correctif : card 0.2.9, styles 0.7. | 29/10/2026 |
| L6-04 | 6 | HACS et lint/format | **Terminé** | Maintenir Black, isort (`--profile black`), flake8 et les quatre workflows CI sur les prochaines évolutions. | 29/10 : fichiers formatés ; configuration `pyproject.toml` ajoutée pour compatibilité Black/isort. Suite complète locale : **449 tests**, **2 154 instructions**, **100 %**, 5 avertissements, 2,26 s, Python 3.14.3. **Confirmation utilisateur GitHub Actions : Lint & Formatting OK, HACS Validate OK, Validate with hassfest OK et Run Tests OK.** | 29/10/2026 |
| L6-05 | 6 | Documentation actualisée dans le dépôt | Terminé | Corriger ensuite les constats devenus obsolètes et le texte sur les plugins. | Documentation intégrée dans le ZIP relu. | 13/10/2026 |
| L6-06 | 6 | Cohérence finale de la documentation | Terminé | Intégrer les fichiers actualisés au dépôt ; maintenir les guides au fil des prochaines évolutions. | Documentation alignée sur 0.2.0, résultat GitHub Actions du 14/10 à 12:15:34, L1-07/L1-09 terminés, L1-06 alors en cours (état historique du 14/10) ; fichiers préparés pour intégration. | 14/10/2026 |
| L6-07 | 6 | Installation, mise à jour et retrait | **En cours — installation neuve validée** | Vérifier la mise à jour de 0.2.2 vers le code actuel 0.2.3 + correctifs, puis les deux options de retrait, uniquement dans HAOS de test. | **29/10 : installation neuve validée par l’utilisateur sur un HAOS vierge de Day Planner. Tous les résultats attendus sont OK : intégration, panneau, configuration vide, 3 capteurs, calendrier, stockage, journaux et Moment conservé après redémarrage.** Code relu : stockage version 1 dans 0.2.2 et 0.2.3. Test de mise à jour documenté, à exécuter ; retrait non testé. | 29/10/2026 |
| L6-08 | 6 | Préparation d'une version propre | À faire | Fixer périmètre, notes de release et limites connues. | Qualification prévue. | 13/10/2026 |
| L6-09 | 6 | Tests de régression de l’exécution et du Journal de bord | Terminé | Maintenir les nouveaux cas lors des évolutions de scripts et des mises à jour HA. | 20/10 : 19 tests ciblés réussis en simulation, modules `action_executor.py` et `logbook.py` à 100 % ciblés ; couverture globale 100 % confirmée ensuite par l’utilisateur. | 20/10/2026 |
| L6-10 | 6 | Atteindre et attester 100 % de couverture sur la reprise eedomus v5.16 | **En cours — validation globale attendue** | Appliquer le complément de 55 tests (quatre modules), relancer la suite entière et enregistrer le nombre réellement obtenu, les instructions, les manquantes et les avertissements. Ne pas imposer de seuil bloquant. | **07/11 : 517 tests réussis ; 2 990 instructions, 243 manquantes, 92 %.** 08/11 : complément préparé, 90 tests ciblés réussis en simulation, mais suite globale HA non revalidée. | 08/11/2026 |
| L7-01 | 7 | Enrichir les propriétés internes du fichier XLSX eedomus | **Reporté — très long terme** | Étudier et renseigner les propriétés du classeur : titre, sujet, description, auteur, mots-clés et autres métadonnées pertinentes, avec données réellement disponibles et sans information inventée. Ne pas modifier l’export actuel. | Décision utilisateur du 07/11/2026 : priorité aux propriétés du **fichier Excel lui-même**, non aux propriétés des objets exposés dans les tableaux. | 07/11/2026 |
| L7-02 | 7 | Réexaminer éventuellement les sept onglets XLSX | **Reporté — très long terme** | Lors de la reprise de L7-01, évaluer si l’organisation, la présentation ou le contenu des onglets mérite des retouches ; aucune refonte décidée aujourd’hui. | Décision utilisateur du 07/11/2026 : export v5.16 conservé en l’état, retouches d’onglets seulement éventuelles. | 07/11/2026 |
| L7-03 | 7 | Qualifier les évolutions futures du classeur | À planifier | Après toute évolution de L7-01/L7-02, vérifier l’ouverture Excel, les métadonnées, la conservation des onglets et l’absence de régression de la reprise eedomus. | Nouveau lot créé le 07/11/2026 ; aucun développement ou essai supplémentaire annoncé à cette date. | 07/11/2026 |

## 5. Lot 1 — Stabiliser le socle

**Statut : partiellement réalisé.** Les corrections déjà intégrées restent enregistrées dans le tableau.

### Intégrité et comportement temporel

- **Terminé le 14/10/2026 :** contrôle des sept références des semaines types et tests des journées inconnues. La finalisation de la vue reste suivie dans le lot 3.


- Exécuter les tests backend existants et les tests WebSocket/API.
- Compléter les fichiers existants pour les corrections apportées.
- Ajouter des tests frontend ciblés si les interactions modifiées le justifient, puis effectuer les essais visuels nécessaires.
- **Terminé le 14/10/2026 :** correction et tests des moments simultanés ; tous les moments d'un même horaire sont traités par le rappel. Conserver les tests de non-régression, sans rouvrir la vue Moments.
- **Terminé le 22/10/2026 (L1-06) :** sept essais réels HA validés : action sur deux helpers et traces, deux moments simultanés, modification d’horaire, exception de calendrier, changement de cycle, passage à minuit et redémarrage avant déclenchement.
- **Terminé le 26/10/2026 (L1-11) :** test réel confirmé d’un événement manqué pendant un arrêt HA : aucun rattrapage rétroactif, reprise de la planification future. Les autres cas d’erreur et de rappels annulés restent couverts par les tests existants.
- **Tests Python terminés le 14/10/2026 :** règle de type cron Debian pour les horaires fixes. Au printemps, les occurrences de l'heure supprimée sont regroupées au premier instant valide (03:00 en Europe/Paris) ; en automne, exécution au premier passage seulement. Les scénarios HA de L1-06 sont validés le 22/10 ; les passages DST restent fondés sur les tests Python, sans essai réel supplémentaire annoncé.

### Ajustements CI et cohérence de version


- **Terminé (L1-07) :** filtres du workflow corrigés et exécution GitHub Actions réussie.
- **Abandonné le 14/10/2026 :** ajout d'un seuil bloquant de couverture. Conserver les mesures et rapports, sans option imposant un seuil.
- **Terminé (L1-07), selon confirmation utilisateur :** présentation du générateur revue, mise à jour du README validée par une exécution du workflow.
- **Terminé le 29/10/2026 (L6-04) :** Black, isort profil black, flake8 et les quatre workflows GitHub Actions (Lint & Formatting, HACS Validate, Validate with hassfest, Run Tests) confirmés OK par l’utilisateur. Conserver ces vérifications en CI.
- **Terminé (L1-09), selon confirmation utilisateur :** manifeste 0.2.0, ancienne constante de version supprimée ; historique du changelog corrigé, avec une seule entrée 0.1.0 datée du 10/10/2026.
- Actualiser les guides et la roadmap : retirer les constats devenus faux sur la CI et les dépendances.
- **Correction prise en compte selon l'utilisateur :** le README décrit le chargement explicite des plugins et identifie les blocs produits par GitHub Actions. Maintenir cette cohérence lors de la validation documentaire finale.
- Préparer une version propre avec notes de release, limites connues et résultats datés.

### Critères de sortie

La configuration invalide est refusée, les événements simultanés sont exécutés correctement et les scénarios temporels retenus sont vérifiés. La CI transmet les échecs et produit les rapports attendus. Les nouvelles vérifications complètent les fichiers de tests existants.

## 6. Lot 2 — Intégrer les Metadata

**Statut : en cours — cœur de la traçabilité validé, qualification d’affichage restant à préciser.**

Le modèle existant `Audit` est conservé (sans renommage imposé vers `Metadata`). Les cinq objets racine persistés portent un audit facultatif avec auteur/date de création et de modification, et les fonctions d’actualisation sont centralisées dans `PlannerEngine`. Les changements d’`Action` et de `ScheduledMoment` actualisent leur parent ; les objets référencés ne changent pas. WebSocket et services privilégient le nom affiché de l’utilisateur, sinon son identifiant ; les Options Flow utilisent `"system"`.

Les données historiques sans audit restent compatibles ; **aucune migration ni invention d’auteur ou de date historique**. En cas de première édition d’un ancien objet, l’audit commence à cette édition. La persistance et les mutations ont été validées par tests et essais Home Assistant du 22 octobre ; il reste à décider ou qualifier l’affichage direct de ces champs dans le panneau et les formulaires. Les essais de reprise/redémarrage avant déclenchement sont validés en L1-06 ; le non-rattrapage d’un événement passé pendant l’arrêt est suivi séparément en L1-11.

## 7. Lot 3 — Simplifier la gestion quotidienne

Les étapes ci-dessous conservent l’ordre demandé pour les vues. Les travaux i18n restent opportunistes.

### 3A. Moments

**Statut : terminé et figé, selon l'état communiqué.**

Périmètre terminé : CRUD, groupes d'actions, détails, traduction Home Assistant, i18n, comptages et gestion des erreurs.

Conserver cette vue comme référence pour les comportements communs des autres vues. Les tests de non-régression restent inclus dans la validation finale. Aucun nettoyage ou travail i18n isolé n'est prévu sur ce bloc.

### 3B. Types de journée

**Statut : terminé ; clôture confirmée par les essais utilisateur.**

CRUD, dépendances, boutons et conservation des saisies validés. Les actions ci-dessous sont conservées comme périmètre de contrôle historique ; elles ne constituent plus une attente sur L3-02.

Périmètre déjà traité : CRUD, moments planifiés, dialogues, validations, i18n, adaptation aux petits écrans, timeline et nettoyage de `day-types-view.js`.

#### Reste à faire

- Effectuer un dernier contrôle global du code actuel et de ses interactions avec la carte et l'API.
- Vérifier l'édition des horaires, les ajouts/suppressions et la cohérence de la timeline après sauvegarde.
- Effectuer un passage de formatage si nécessaire.
- Traiter une traduction uniquement si le fichier ou dialogue est déjà retouché.

#### Critère de sortie

Les parcours de gestion des journées et de leurs moments planifiés sont cohérents, sans régression connue. Le code est relu et formaté si nécessaire. Une traduction restante ne bloque pas la clôture.

### 3C. Semaines types

**Statut : terminé ; quatre essais HA et affichage des erreurs dans les dialogues validés.**

Les travaux ci-dessous sont conservés comme périmètre de référence et de non-régression.

#### Travaux

- Relire et finaliser création, modification et suppression.
- Vérifier l'affectation des sept jours à des types de journée existants.
- **Terminé le 14/10/2026 (L1-04) :** validation métier des références des semaines. Conserver cette règle pendant les retouches de la vue ; vérifier la présentation des erreurs dans l'interface.
- Vérifier les dépendances avec les cycles et expliquer les suppressions bloquées.
- Harmoniser les dialogues, les erreurs et le comportement sur petits écrans.
- Nettoyer le code de la vue et les interactions associées.
- Compléter l'i18n uniquement au fil des retouches.

#### Critères de sortie

- Les sept affectations sont conservées après sauvegarde et rechargement.
- Une journée inconnue est refusée par les différents chemins de modification.
- Une semaine utilisée par un cycle ne peut pas être supprimée et l'interface explique pourquoi.
- Les parcours principaux restent utilisables sur ordinateur et mobile.
- Les tests concernés sont complétés dans `test_validator.py`, `test_engine.py`, `test_websocket_api.py` et les tests de services/options selon les changements.

### 3D. Cycles

**Statut : terminé ; essais HA validés le 18 octobre et corrections de robustesse relues le 19 octobre.**

Les travaux ci-dessous restent le périmètre de référence. Les essais temporels du planificateur sont suivis séparément dans L1-06.

#### Travaux

- Relire et finaliser création, modification et suppression.
- Vérifier la séquence ordonnée de 1 à 4 semaines types.
- Vérifier la date de début un lundi et l'unicité des dates de début.
- Distinguer clairement le nombre de semaines d'un cycle de la limite du nombre de cycles enregistrés.
- Vérifier références, dépendances, erreurs et cohérence de la résolution du cycle applicable.
- Finaliser l'UX des formulaires et l'affichage sur petits écrans.
- Compléter l'i18n lors des retouches nécessaires.

#### Critères de sortie

Un cycle valide est sauvegardé et résolu correctement ; les entrées invalides sont refusées avec une erreur compréhensible. Les limites et dépendances sont cohérentes entre interface, services, WebSocket et moteur.

### 3E. Calendrier / Exceptions

**Statut : terminé ; tous les essais fonctionnels HA confirmés le 19 octobre.**

La description reste facultative ; une chaîne vide est transmise à l’API. Les brouillons conservent les saisies après erreur. Création, modification, effacement de description et suppression avec retour au cycle sont validés. Les travaux ci-dessous restent le périmètre de référence ; la qualification transversale reste ouverte ; L1-06 est clôturé le 22/10.

#### Travaux

- Finaliser la vue calendrier, la navigation et les détails du jour sélectionné.
- Vérifier création, modification et suppression des exceptions.
- Vérifier la priorité des exceptions et l'unicité d'une exception par date.
- Montrer le contexte issu des cycles et le type de journée effectivement appliqué.
- Vérifier les mises à jour après changement d'un cycle, d'une semaine ou d'une journée.
- Vérifier la cohérence entre timeline, calendrier Home Assistant et événements exécutés.
- Finaliser l'adaptation aux petits écrans ; traiter l'i18n lors des retouches.

#### Critères de sortie

L'ajout, l'édition et le retrait d'une exception actualisent correctement le planning. La vue et les entités présentent un contexte cohérent, y compris sans cycle applicable.

### 3F. Passage transversal final

**Statut : L3-06 terminé le 23/10, L3-07 et L3-08 qualifiés le 24/10 ; droits avancés reportés en L3-12.** Première série de six corrections terminée et vérifiée sur le dernier fichier le 19 octobre : protection de l’édition cycle lors des actualisations HA, gardes des cinq opérations restantes, désactivation des boutons cycles, rendu final des exceptions, gestionnaire de suppression cycle unique et ordre des validations de date. Les contrôles syntaxiques passent. Aucun nouveau résultat de suite Python ni essai complet clavier/mobile/cache/permissions n’est déduit de cette relecture.

#### Travaux

- Recenser les onglets en français en dur et les messages généraux : « Chargement… », erreurs globales et navigation. Traduire lorsque les composants sont déjà retouchés ; ne pas en faire une condition de sortie.
- Réduire les doublons CSS/JS identifiés sans rouvrir inutilement les vues figées.
- **L3-06 terminé :** cohérence des messages, conservation des champs après erreur, correction/enregistrement et annulation sans effet. Les fenêtres testées n’ont pas de croix de fermeture (contrôle non applicable). Maintenir cette garantie lors des futures évolutions.
- **L3-07 terminé le 24/10 :** anomalie initiale de focus/Tab/Échap constatée sur tous les formulaires. Premier correctif régressif (clic/saisie bloqués et navigation basculant vers le navigateur), puis correctifs v2/v3 validés progressivement par l’utilisateur dans Home Assistant : clic/saisie rétablis, focus initial dans le premier champ, navigation clavier correcte, affichage mobile OK et Échap opérationnel. Les regressions du premier correctif ne doivent pas être réintroduites. Conserver le retour du focus et les cas de sélecteurs complexes dans les vérifications de non-régression si les formulaires évoluent.
- Maintenir l’accessibilité validée (focus initial, navigation clavier et Échap) ; vérifier les éventuels nouveaux libellés et boutons au fil des modifications.
- Affichage mobile des fenêtres testé et validé le 24/10 ; poursuivre les contrôles spécifiques de la carte Lovelace si elle évolue (L6-03).
- **L3-08 validé :** après mise à jour et redémarrage HA, le frontend charge les fichiers actualisés avec un rechargement simple de la page. Conserver les tests de non-régression.
- **L3-08 qualifié :** compte HA non administrateur testé en consultation, ajout, modification et suppression. La création de profils gestionnaires / lecteurs et le contrôle côté backend sont reportés à L3-12.

#### Critère de sortie

Les vues ont des comportements communs cohérents et restent accessibles. La mise à jour du frontend ne laisse pas un ancien code en cache dans les scénarios vérifiés. Les écarts i18n non traités restent recensés.

### 3G. Duplication de tous les objets — L3-10

**Statut : Terminé le 28 octobre 2026, après démarrage le 27 octobre.** La duplication des Moments (avec reprise des actions) est **validée dans Home Assistant pour l’enregistrement et l’annulation**. La duplication d’une Action dans le même Moment et celle des Types de journée (affectations et horaires) ont également été validées en HA. La duplication des Moments planifiés a été retirée du périmètre sur décision utilisateur du 27/10 : le bouton ouvrait un formulaire d’ajout d’un autre Moment, sans véritable copie du Moment source. La création ordinaire reste disponible. **La duplication des Semaines types et celle des Cycles sont validées en HA le 28/10.** La duplication des **Exceptions de calendrier** est validée en HA le 28/10, comme les cinq autres familles retenues. Ajout demandé le 22 octobre 2026. Cette fonctionnalité complète les commandes de gestion existantes (« Éditer/Modifier » et « Supprimer ») sans rouvrir les validations déjà acquises. Cette clôture porte sur les essais fonctionnels HA communiqués, et non sur une nouvelle livraison ou une suite Python complète.

#### Périmètre de l'action « Dupliquer »

- **Moments :** créer un nouveau moment à partir d'un existant ; reprendre son nom, son icône et ses actions. Générer de nouveaux identifiants pour le moment et pour les actions copiées. Les références des journées vers le moment source restent inchangées.
- **Actions d'un moment :** dupliquer une action (libellé et séquence Home Assistant) dans le même moment, avec un identifiant d'action distinct ; aucune exécution lors de la copie.
- **Types de journée :** reprendre les horaires et les moments planifiés dans un nouveau type de journée ; copier les entrées enfants avec de nouveaux identifiants si nécessaire, tout en conservant les références vers les moments existants.
- **Moments planifiés : exclus de « Dupliquer »** sur décision utilisateur du 27/10. Conserver l’ajout, la modification et la suppression. Le même `moment_id` ne peut pas être affecté deux fois à une journée ; le bouton ajouté ouvrait simplement la création d’une autre affectation, ce qui ne constitue pas la duplication souhaitée.
- **Semaines types :** reprendre les sept affectations de types de journée dans une nouvelle semaine, sans copier physiquement les types de journée référencés.
- **Cycles :** reprendre la séquence ordonnée des semaines types ; exiger une nouvelle date de début valide (lundi et date distincte), respecter le nombre maximal de cycles configuré et les références existantes.
- **Exceptions de calendrier :** reprendre type de journée et description, mais exiger une autre date afin d'éviter deux exceptions pour la même journée.

#### Comportement commun attendu

1. Afficher « Dupliquer » à côté des actions existantes de gestion, dans les écrans concernés. Préremplir un formulaire de création à partir de la source et laisser corriger les valeurs avant validation (nom, date, heure, autres champs selon l'objet).
2. Créer un **nouvel objet distinct** : identifiants uniques et métadonnées d'audit de création fraîches (acteur et horodatage courants), sans reprendre l'historique `Audit` de la source.
3. Conserver l'objet source, ses références et les liens existants ; une copie ne doit pas déplacer, modifier ou supprimer la source, ni déclencher immédiatement les actions Home Assistant.
4. Utiliser les mêmes règles métier et contrôles de référence que la création normale ; signaler les collisions d'identifiant, de date, les limites de cycles et les références invalides. Conserver le formulaire prérempli si la création échoue.
5. Réutiliser la chaîne de persistance, notification et replanification habituelle après réussite ; actualiser les vues. Une annulation ne doit rien écrire.
6. Compléter les tests existants (`test_engine.py`, `test_validator.py`, `test_websocket_api.py`, tests services/options concernés) et les parcours HA, avec non-régression des opérations Modifier et Supprimer.

#### Critères de sortie

Les six familles retenues (Moments, Actions, Types de journée, Semaines types, Cycles et Exceptions) sont duplicables depuis leur gestion ; les Moments planifiés restent gérés via Ajouter/Modifier/Supprimer, avec des identifiants valides, sans modifier la source, avec un nouvel audit ; les cas de limites, erreurs API, annulation, dépendances et rafraîchissement sont testés. Les éléments de structure réutilisables restent des références ; les contenus enfants propres à une copie sont indépendants.

### Améliorations ultérieures conservées

**Évolution très long terme — propriétés du classeur XLSX de reprise eedomus (décision du 07/11/2026 ; suivie désormais dans le lot 7, L7-01 à L7-03).**

- **Conserver l’export actuel en l’état** : les sept onglets de la v5.16 et leur contenu ne sont pas à modifier dans les correctifs en cours.
- **Objectif principal pour plus tard : enrichir les propriétés du fichier XLSX lui-même**, c’est-à-dire ses métadonnées (par exemple titre, sujet, description, auteur et mots-clés), et non enrichir en priorité les propriétés des objets Day Planner présentés dans les tableaux.
- **Objectif secondaire éventuel** : retoucher l’organisation, la présentation ou le contenu des onglets si le besoin se confirme à ce moment-là.
- **Priorité : très basse ; échéance : non planifiée.** Ce sujet reste distinct des corrections fonctionnelles et des validations de la reprise eedomus.

L'ajout guidé des moments prédéfinis reste distinct (L3-11). Import/export, profils multiples et synchronisation bidirectionnelle ne font pas partie du périmètre immédiat.


## 8. Lot 4 — Ajouter les horaires avancés

**Statut : à planifier ; périmètre à préciser.**


Faire évoluer `TimeDefinition` au-delà de `fixed_time`, avec un premier périmètre à préciser, par exemple lever/coucher du soleil et décalages. Définir les horaires indisponibles, les passages de date et la cohérence entre calcul, affichage et exécution.

Validation attendue : compatibilité des horaires fixes et résultats cohérents dans toutes les interfaces.

## 9. Lot 5 — Ajouter une source de calendrier externe

**Statut : à planifier.**


Prévoir une source externe, notamment Google Calendar, après définition des règles de correspondance et de synchronisation. La première version en lecture seule et la priorité locale → externe → cycle restent des propositions à valider.

Définir conflits, événements sur plusieurs jours, fuseaux horaires, origine des exceptions, absence de doublons et comportement en cas d'indisponibilité. Une synchronisation ne doit pas altérer les exceptions locales.

## 10. Lot 6 — Qualifier la première version stable

**Statut : validation finale à réaliser après consolidation des vues et corrections nécessaires du lot 1.**

### Travaux


- Exécuter les tests backend existants et les tests WebSocket/API.
- Compléter les fichiers existants pour les corrections apportées.
- Ajouter des tests frontend ciblés si les interactions modifiées le justifient, puis effectuer les essais visuels nécessaires.
- **Terminé le 14/10/2026 :** correction et tests des moments simultanés ; tous les moments d'un même horaire sont traités par le rappel. Conserver les tests de non-régression, sans rouvrir la vue Moments.
- **Terminé le 22/10/2026 (L1-06) :** sept essais réels HA validés : action sur deux helpers et traces, deux moments simultanés, modification d’horaire, exception de calendrier, changement de cycle, passage à minuit et redémarrage avant déclenchement.
- **Terminé le 26/10/2026 (L1-11) :** test réel confirmé d’un événement manqué pendant un arrêt HA : aucun rattrapage rétroactif, reprise de la planification future. Les autres cas d’erreur et de rappels annulés restent couverts par les tests existants.
- **Tests Python terminés le 14/10/2026 :** règle de type cron Debian pour les horaires fixes. Au printemps, les occurrences de l'heure supprimée sont regroupées au premier instant valide (03:00 en Europe/Paris) ; en automne, exécution au premier passage seulement. Les scénarios HA de L1-06 sont validés le 22/10 ; les passages DST restent fondés sur les tests Python, sans essai réel supplémentaire annoncé.


- **Terminé (L1-07) :** filtres du workflow corrigés et exécution GitHub Actions réussie.
- **Abandonné le 14/10/2026 :** ajout d'un seuil bloquant de couverture. Conserver les mesures et rapports, sans option imposant un seuil.
- **Terminé (L1-07), selon confirmation utilisateur :** présentation du générateur revue, mise à jour du README validée par une exécution du workflow.
- **Terminé le 29/10/2026 (L6-04) :** Black, isort profil black, flake8 et les quatre workflows GitHub Actions (Lint & Formatting, HACS Validate, Validate with hassfest, Run Tests) confirmés OK par l’utilisateur. Conserver ces vérifications en CI.
- **Terminé (L1-09), selon confirmation utilisateur :** manifeste 0.2.0, ancienne constante de version supprimée ; historique du changelog corrigé, avec une seule entrée 0.1.0 datée du 10/10/2026.
- Actualiser les guides et la roadmap : retirer les constats devenus faux sur la CI et les dépendances.
- **Correction prise en compte selon l'utilisateur :** le README décrit le chargement explicite des plugins et identifie les blocs produits par GitHub Actions. Maintenir cette cohérence lors de la validation documentaire finale.
- Préparer une version propre avec notes de release, limites connues et résultats datés.

- Tester les migrations sur des copies de configurations réalistes.
- Prévoir une période d’observation de deux semaines avec un planning représentatif si nécessaire à la qualification.
- Fixer le périmètre exact de la version stable et la compatibilité déclarée.

### Critères de sortie


- Suite complète réussie ; couverture mesurée et rapportée, avec un objectif de 100 % sans exclusions artificielles. Aucun seuil bloquant de couverture n'est imposé.
- Aucun défaut connu provoquant perte de données ou déclenchement incorrect dans le périmètre retenu.
- Parcours CRUD, modales et affichages validés sur ordinateur et mobile.
- Installation neuve, mise à jour et retrait avec/sans suppression vérifiés.
- Vérifications HACS et lint/format réussies ; documentation cohérente avec la version livrée.
- Les traductions non prioritaires ne bloquent pas la publication ; elles restent suivies.

## 11. Lot 7 — Enrichir les propriétés du classeur XLSX eedomus

**Statut : reporté — très long terme ; priorité très basse, sans échéance ni version cible.** Ce lot est ajouté aux six lots initiaux sans changer leurs numéros ni leurs priorités.

### Référence actuelle à conserver

Le téléchargement du classeur XLSX lors de la reprise eedomus existe en **v5.16**, avec **sept onglets** : Résumé, Toutes associations, Prises en charge, Ignorées, Éléments non repris, Moments et actions, Journées et horaires. **L’export reste en l’état** : il n’est pas prévu de modifier ces onglets ni de réécrire le générateur dans les correctifs actuels. La validation globale de la v5.16 dans HA OS ne doit pas être confondue avec les tests isolés du générateur.

### Travaux envisagés

- **L7-01 — Objectif principal : enrichir les propriétés du fichier XLSX lui-même.** Étudier le titre, le sujet, la description, l’auteur, les mots-clés et, selon leur pertinence, les autres métadonnées natives du classeur. N’utiliser que des valeurs fiables et disponibles ; ne pas inventer de dates, d’auteurs ou de détails personnels.
- **L7-02 — Objectif secondaire, facultatif : retoucher les onglets.** Évaluer plus tard la présentation, la structure ou le contenu des sept feuilles, uniquement si un besoin concret est confirmé. Aucune retouche décidée pour le moment.
- **L7-03 — Qualification lors de la reprise des travaux.** Contrôler la lecture dans Excel et les lecteurs compatibles, la présence des propriétés attendues, la conservation des données existantes et les tests de non-régression des exports. Suivre les résultats dans les modules de test existants et maintenir l’objectif de couverture du projet sans seuil bloquant.

### Critères de sortie futurs

Les propriétés du classeur sont renseignées de manière explicite et fiable, sans perte des sept onglets et sans changement du comportement d’import eedomus. Les éventuelles modifications de présentation ne seront engagées qu’après nouvelle décision. **Aucun travail immédiat ni livraison supplémentaire n’est impliqué par l’ouverture de ce lot.**

## 12. Mise à jour du suivi et journal conservé

À chaque mise à jour :

1. Lire la version courante et conserver toutes les lignes et tous les identifiants du tableau.
2. Actualiser les statuts uniquement avec une indication utilisateur ou un résultat vérifié ; préciser leur origine.
3. Actualiser le reste à faire, la preuve et la date des lignes concernées.
4. Ajouter les nouveaux points avec un identifiant inédit, sans renuméroter les précédents.
5. Ajouter une entrée au journal ci-dessous pour les changements significatifs ; les entrées historiques restent conservées.
6. Conserver les points terminés, reportés ou abandonnés avec leur décision. Si une tâche est scindée, conserver sa ligne et référencer les nouvelles lignes.

Les critères des lots peuvent être précisés et de nouvelles tâches ajoutées. Les travaux décidés ne sont pas retirés silencieusement. Le suivi hebdomadaire reprend les changements significatifs du tableau.

| Date | Mise à jour / décision |
| --- | --- |
| 12/10/2026 | Création de la roadmap initiale en six lots. |
| 13/10/2026 | Relecture du nouveau ZIP : adaptations CI et tests intégrées ; défauts de références des semaines et de moments simultanés reproduits. |
| 13/10/2026 | Statuts utilisateur intégrés : moments terminés et figés ; journées presque terminées ; semaines, cycles puis calendrier à finaliser. i18n non prioritaire. |
| 13/10/2026 | Retour à la structure en six lots ; création du tableau permanent avec identifiants stables et règle de conservation des lignes. |
| 14/10/2026 | L1-04 et L1-05 passent à Terminé : références des sept jours validées et moments simultanés corrigés. Données des anciens tests adaptées ; 29 tests des planificateurs réussis. |
| 14/10/2026 | Nouveau résultat utilisateur de référence : 403 tests réussis, 1 896 instructions mesurées, aucune non couverte, 100 % de couverture, 5 avertissements en 1,22 s. L6-01 actualisé et L6-02 terminé pour cet état du code. |
| 14/10/2026 | L1-08 passe à Abandonné : seuil bloquant de couverture refusé par l'utilisateur. Mesure et rapports conservés, sans seuil bloquant dans les commandes ni dans la CI. |
| 14/10/2026 | Calcul autour de minuit et trois tests de changement d'heure réussis. Règle retenue : rattrapage au printemps à la première heure valide et exécution unique au premier passage en automne ; pas de rattrapage général après un arrêt. |
| 14/10/2026 | Résultat utilisateur actualisé : 407 tests réussis, 1 908 instructions mesurées, aucune non couverte, 100 %, 5 avertissements en 1,22 s. L1-06 passe à En cours : essais réels HA encore à confirmer. |
| 14/10/2026 | Rappel créé pour les essais réels HA le 15 octobre vers 18 h (Europe/Paris). Documentation et suivi actualisés, sans suppression des lignes. |

| 14/10/2026 | L1-07 terminé : workflow tests.yml exécuté avec succès et README généré à 12:15:34 ; 407 tests, 1 908 instructions et 100 % de couverture. |
| 14/10/2026 | Publication 0.2.0 réussie après rétablissement du lien avec l'historique de la release 0.1.0. La version publiée devient 0.2.0 ; cela ne valide pas le lot Metadata. |
| 14/10/2026 | L1-09 terminé selon confirmation utilisateur : référence de version dans le manifeste et nettoyage du changelog d'après le tag 0.1.0 du 10 octobre. L1-06 reste En cours pour les essais réels HA. |

| 14/10/2026 | L6-06 : documentation alignée sur la version publiée 0.2.0 et le résultat GitHub Actions à 12:15:34. Les guides distinguent Python local 3.14.3 et CI 3.14.8, clôturent L1-07/L1-09 et conservent les essais HA ouverts. Fichiers préparés pour intégration au dépôt. |

| 19/10/2026 | L3-02 et L3-03 clôturés d’après les essais HA : saisies conservées, CRUD, dépendances et erreurs visibles. |
| 19/10/2026 | L3-04 clôturé : essais des cycles validés le 18/10, puis corrections de robustesse vérifiées dans le fichier du 19/10. |
| 19/10/2026 | L3-05 clôturé après confirmation de tous les essais HA : description dans le champ, description vide acceptée, édition et suppression, exception appliquée puis retour au cycle. |
| 19/10/2026 | Relecture de 14 fichiers frontend : 12 JS et 2 JSON syntaxiquement valides. Six corrections transversales relues dans le dernier day-planner-card.js ; L3-06, L3-07 et L6-03 restent en cours pour leurs contrôles restants. |
| 19/10/2026 | L1-06 explicitement maintenu en cours. Les 407 tests Python et 100 % de couverture restent le résultat communiqué du 14/10, sans nouvelle exécution. Aucun rappel créé ou reprogrammé dans cette mise à jour. |
| 20/10/2026 | L1-10 : journalisation renforcée des actions et cibles indisponibles ; avertissements `homeassistant.helpers.service` recopiés en ERROR Day Planner sans supprimer le WARNING HA. Événement `day_planner_action` avant le service et contexte partagé pour l’attribution Logbook. |
| 20/10/2026 | Validation fonctionnelle Logbook : événement source « Day Planner — action XX1 test (id : XX1) », puis transition de `input_boolean.day_planner_test` de Activé à Désactivé avec cette action comme cause. Le message « Aucune cause... » sur l’événement racine est normal. |
| 20/10/2026 | L6-09 et L6-01 : ajout de tests des branches défensives (9 lignes manquantes sur 2 093 instructions au rapport intermédiaire) ; 19 tests ciblés réussis en simulation et 100 % de couverture globale confirmé par l’utilisateur. Nombre exact de tests du dernier rapport non communiqué. L1-06 conserve son statut En cours. |
| 21/10/2026 | Audit étendu aux modèles `Moment`, `WeekSchedule`, `Cycle` et `CalendarException`, après `DayType` ; fonctions centralisées dans `PlannerEngine`. Validation progressive des tests dans les fichiers existants, sans patch et sans migration. Dernier rapport complet chiffré : 449 tests, 2 146 instructions, 0 non couverte, 100 % de couverture. |
| 21–22/10/2026 | WebSocket et services HA transmettent l’auteur réel lorsqu’il est disponible ; Options Flow utilise explicitement `"system"`. Création/modification d’Actions et Moments planifiés attribuées à leur parent. Tests validés successivement. |
| 22/10/2026 | Contrôles fonctionnels Home Assistant confirmés par l’utilisateur pour Moments, Actions, Types de journée, Moments planifiés, Semaines types, Cycles et Exceptions. L2-01 et L2-03 terminés ; L2-02 reste ouvert uniquement pour l’affichage détaillé des métadonnées et qualification associée. Aucune migration d’audit. |
| 22/10/2026 | Extension fonctionnelle décidée : opération « Dupliquer » sur toutes les familles gérées (Moments, Actions, Types de journée, Moments planifiés, Semaines types, Cycles et Exceptions), en complément des opérations de modification/suppression. L3-10 élargi ; création de L3-11 pour conserver le sujet historique des moments prédéfinis guidés. Statut : À planifier ; aucun code déclaré modifié. |
| 22/10/2026 | **L1-06 clôturé** après confirmation utilisateur des sept scénarios HA (deux helpers et traces, deux moments simultanés, replanification horaire, exception, changement de cycle, passage à minuit, redémarrage avant événement). Le test de non-rattrapage après un arrêt couvrant un événement n’a pas été annoncé : suivi explicite L1-11 « À confirmer » ; aucune nouvelle exécution de pytest attribuée à cette validation. L3-06 devient la prochaine priorité. |

| 23/10/2026 | **L3-06 clôturé** après retours utilisateurs : affichage du message de limite à 4 cycles, conservation des saisies lors d’une erreur, possibilité de corriger puis enregistrer, annulation sans modification. Pas de croix de fermeture sur les fenêtres : contrôle non applicable, sans nouveau test requis. Prochaine priorité L3-07 (focus, clavier, libellés et responsive), en lien avec L6-03. |

| 22–23/10/2026 | **L3-07 : défaut de navigation clavier identifié sur l'ensemble des formulaires modaux.** Les onglets de fond reçoivent le focus avant la fenêtre ; Échap ne ferme pas. Patch commun préparé, contrôle syntaxique et `git apply --check` réussis sur le JS de la bibliothèque (19/10). Essais HA indispensables avant validation ou clôture du lot. |

| 24/10/2026 | **L3-07 clôturé** après validation utilisateur dans HA : souris et saisie fonctionnent après correction v2, focus initial correct avec v3, navigation Tab/Maj+Tab correcte, affichage mobile réel OK, touche Échap opérationnelle. Le premier patch avait bloqué clic et saisie et ne doit pas être réintroduit. L3-08 est le prochain point à traiter. Aucun nouveau total pytest n’est attribué à ces essais manuels. |

| 24/10/2026 | **L3-08 qualifié** : simple rechargement après mise à jour/redémarrage HA fonctionne ; un compte non administrateur peut consulter, ajouter, modifier et supprimer. Étude d’impact des droits fins réalisée ; **L3-12 reporté** par décision utilisateur jusqu’à la finalisation des autres fonctionnalités. Aucun changement de permissions. |

| 26/10/2026 | **L1-11 clôturé** après confirmation utilisateur du test HA : événement tombant pendant un arrêt non rattrapé au redémarrage, prochain événement futur replanifié et continuité assurée. **L3-10** devient le prochain chantier ; aucune duplication annoncée comme implémentée. |
| 27/10/2026 | **L3-10 en cours** : premier patch ciblé Moments + copie des actions préparé à partir du JS de bibliothèque du 19/10 enrichi des correctifs L3-07 v1/v2/v3. Contrôles de syntaxe, application et scénarios isolés Node réussis ; en attente des essais Home Assistant. Aucun test Python supplémentaire ni livraison confirmée. |
| 27/10/2026 | **L3-10 — Moments confirmés en HA** par l’utilisateur : duplication avec enregistrement ou annulation OK. Nouvelle étape **Actions isolées** : patch JS ciblé préparé pour `day-planner-card.js` et testé hors HA (bouton, séquence clonée, collisions d’identifiants, sauvegarde, annulation, erreurs). Essai réel et contrôle de non-régression restent à faire avant validation de cette étape. |

| 27/10/2026 | **L3-10 — Actions confirmées en HA** : utilisateur indique tests 4 et 5 OK (duplication enregistrée et annulation sans création). Nouveau patch **Types de journée** préparé, réutilisant les commandes WebSocket d’ajout et suppression ; reprise des affectations et de leurs heures, sans créer les Moments référencés, avec tentative de nettoyage d’une copie partielle. Syntaxe et tests isolés Node vérifiés, essai HA à faire. |

| 27/10/2026 | **L3-10 — Types de journée validés en HA** : tous les tests convenus sont OK selon l’utilisateur (copie, sauvegarde, annulation). Étape suivante **Moments planifiés** : la validation du backend interdit de réutiliser le même `moment_id` dans une journée. Patch uniquement `day-planner-card.js` : bouton Dupliquer dans la fenêtre d’édition, heure préremplie, sélection d’un autre Moment non utilisé ; bouton désactivé si aucun disponible. Aucun changement du backend ni du Moment source. Syntaxe et tests isolés Node OK ; essai HA requis. |

| 27/10/2026 | **L3-10 — décision de retrait de « Dupliquer » pour les Moments planifiés.** Test utilisateur dans la timeline : la duplication proposée ouvrait l’ajout d’un autre Moment et d’un horaire, sans véritable duplication de l’affectation. Demande explicite : supprimer ce bouton. Retour au comportement antérieur via patch inverse ne touchant que `day-planner-card.js` ; Moments, Actions et Types de journée conservés. **Retrait confirmé OK dans HA** le 27 octobre. |

| 27/10/2026 | **L3-10 — duplication des Semaines types à tester dans HA.** Nouveau patch ciblé dans `day-planner-card.js` et `views/week-schedules-view.js`. Le bouton Dupliquer ouvre le formulaire de création avec un nouvel identifiant, un libellé suffixé « (copie) » et les 7 types de journée référencés ; il ne recopie pas les types de journée eux-mêmes et réutilise l'API d'ajout. Contrôle de syntaxe JS, de patch et scénarios isolés Node (affichage, préremplissage, collisions, enregistrement, annulation, erreur API) réussis. Aucune modification Python ; essai réel HA encore nécessaire. |

| 28/10/2026 | **L3-10 — Semaines types validées en HA** : tous les essais demandés ont réussi (sept affectations recopiées, copie indépendante, enregistrement et annulation). **Duplication des Cycles à tester** : patch frontend ciblé (`day-planner-card.js`, `views/cycles-view.js`) ; nouveau nom et ID, mêmes références ordonnées aux semaines types, date de début laissée vide afin d'exiger un lundi distinct ; création via l'API existante, respect des validations et limites backend. Contrôles syntaxiques et tests isolés Node réussis. Aucun changement Python ; essai HA requis. |
| 28/10/2026 | **L3-10 — Duplication des Cycles validée en HA** : utilisateur confirme « test ok » après le patch de duplication. **Exceptions de calendrier à tester** : patch frontend ciblé (`day-planner-card.js`, `views/calendar-view.js`), ajout du bouton Dupliquer dans les actions de l'exception du jour sélectionné ; copie du type de journée et de la description ; nouvelle date obligatoire, unique, sans reprise de la date source ; ID créé selon le schéma actuel `exception-AAAA-MM-JJ`. Après enregistrement, affichage du mois et de la nouvelle date. Refus des dates invalides ou occupées, conservation des champs après erreur, annulation sans écriture. Syntaxe, contrôle du patch et 10 tests isolés Node validés ; essai HA encore requis, pas de modification backend. |


| 28/10/2026 | **L3-10 clôturé** après validation HA de la duplication des Exceptions de calendrier (« test OK » de l’utilisateur). La duplication des six familles retenues est désormais validée : Moments, Actions, Types de journée, Semaines types, Cycles et Exceptions. La duplication des Moments planifiés reste délibérément supprimée. Aucun nouveau total pytest ni publication affirmé. Prochaine priorité : L6-03, contrôles transversaux frontend et non-régression après cumul des patchs, puis L6-04, HACS et lint/format. |
| 28/10/2026 | **L6-03 : syntaxe du frontend contrôlée** par l’utilisateur : 12 fichiers `.js` et 2 fichiers `.json` valides. Navigation entre les vues contrôlée ; suppression refusée pour un Type de journée référencé par une Semaine type ou une exception, protections backend conservées. |
| 29/10/2026 | **L6-03 : Types de journée validés dans HA** après correctifs fondés sur le ZIP 0.2.3 : ordre alphabétique dans Ajouter un Moment OK ; compteurs et détails des utilisations présents ; refus de suppression avec références OK ; multilingue FR/EN OK. Ergonomie initiale des détails au clic signalée comme peu pratique, remplacée par infobulles au survol ; dernier test utilisateur « test ok ». L6-03 passe à **Terminé**. Les versions frontend modifiées ont été incrémentées (card 0.2.9, styles 0.7) sans modification du manifeste ni nouvelle publication. |
| 29/10/2026 | **L6-04 démarre** : trois workflows du ZIP 0.2.3 identifiés (Lint & Formatting, HACS Validate, Validate with hassfest) ; exécution locale en lecture seule de Black/isort/flake8 puis vérification des workflows GitHub Actions à effectuer. Les résultats ne sont pas encore confirmés. |
| 29/10/2026 | **L6-04 — Formatage local et tests Python validés.** Black a identifié cinq fichiers à reformater ; l’utilisateur a corrigé les imports en harmonisant isort via `--profile black` et un `pyproject.toml`, puis confirmé la réussite de Black, isort et flake8 pour tous les fichiers. La suite complète a réussi : **449 tests**, **2 154 instructions**, **0 manquante**, **100 % de couverture**, **5 avertissements**, **2,26 s**, **Python 3.14.3**. Le résultat du 21/10 (2 146 instructions) reste conservé. **HACS Validate, hassfest et workflows GitHub Actions restent à confirmer** ; aucune clôture anticipée. |

| 29/10/2026 | **L6-04 clôturé sur confirmation utilisateur GitHub Actions** : 1) Lint & Formatting OK ; 2) HACS Validate OK ; 3) Validate with hassfest OK ; 4) Run Tests OK. Le formatage local Black/isort/flake8 et les 449 tests Python à 100 % avaient déjà été validés. Aucune nouvelle release ni version publiée n’est déduite de ces succès. **Prochaine priorité : L6-07 (installation, mise à jour, retrait) en environnement de test.** |

| 29/10/2026 | **L6-07 — lancement de la qualification installation neuve.** Scénario HA de test documenté à partir du ZIP source 0.2.3 relu : installation depuis l’état actuel du dépôt (L6-03 intégré), config entry unique, configuration initialement vide, création du stockage, panneau, trois capteurs et calendrier. Éléments attendus identifiés par lecture de `__init__.py`, `config_flow.py`, `storage.py`, `sensor.py` et `calendar.py`. **Tests manuels encore à effectuer ; aucune modification du code.** La mise à jour et le retrait suivront. |

| 29/10/2026 | **L6-07 — installation neuve validée en conditions réelles** : l’utilisateur confirme l’installation réussie sur un HAOS vierge de Day Planner et l’ensemble des résultats attendus, y compris intégration unique, panneau, configuration vide, 3 capteurs, calendrier, stockage, absence d’erreur de chargement et persistance d’un Moment au redémarrage. Le scénario 1 est clos ; le scénario 2 (mise à jour 0.2.2 vers état actuel 0.2.3 + correctifs) est préparé, sans exécution annoncée. Le retrait reste à tester. |
| 07/11/2026 | **Création du lot 7**, sans toucher aux six lots historiques : export XLSX eedomus v5.16 conservé avec ses sept onglets. **L7-01** (enrichir avant tout les propriétés du fichier XLSX), **L7-02** (éventuelles retouches des onglets) et **L7-03** (qualification future) ajoutés au tableau permanent. Sujet reporté à très long terme, sans date ni développement immédiat. |

### Contrôles L6-04 — bilan final au 29 octobre 2026

- **Terminé en local :** Black/isort/flake8. Les cinq fichiers initialement refusés par `black --check` ont été formatés ; conflit de style d’import résolu via `--profile black` dans les commandes isort et via `pyproject.toml` (profil black). L’utilisateur confirme tous les fichiers conformes.
- **Terminé en local :** suite pytest complète après formatage, **449 tests réussis, 2 154 instructions, 0 manque, 100 %**, 5 warnings en 2,26 s (Python 3.14.3). Pas de seuil `--cov-fail-under=100` imposé.
- **Terminé en CI le 29/10 :** `Lint & Formatting`, `HACS Validate`, `Validate with hassfest`, `Run Tests` : **tous OK**, selon confirmation de l’utilisateur sur GitHub Actions.
- **L6-04 clôturé :** maintenir ces contrôles à chaque évolution ; tout échec ultérieur sera traité fichier par fichier.


### L6-07 — installation neuve, résultat du 29 octobre

- **Validé sur HAOS de test** : tous les résultats du scénario d’installation neuve ont été confirmés par l’utilisateur, y compris conservation d’un Moment après redémarrage.
- **À tester ensuite** : reprise des données lors d’une mise à jour depuis une version antérieure sur HAOS isolé, puis retrait avec ou sans suppression volontaire.
- **Aucune évolution du code** attribuée à cette validation.

| 08/11/2026 | **L6-10 ouvert** : la couverture de la reprise eedomus v5.16 reste à confirmer en suite complète. Dernier rapport utilisateur : 517 tests, 2 990 instructions, 243 manquantes, 92 %. Complément ciblé de 55 tests préparé (extracteur, importeur, Excel, Options Flow), sans modification du code de production ni exclusion. Documentation fonctionnelle, technique, tests et export XLSX réconciliée avec la v5.16, sans modifier le lot 7 reporté. |

## 13. Prochaine étape

**Validation immédiate L6-10 :** relancer la suite pytest complète après intégration des quatre fichiers de tests, vérifier le résultat global et les manquantes, puis seulement actualiser les chiffres de référence et les blocs statistiques générés par CI. **Ne pas confondre « tests ciblés 100 % » et « projet global 100 % ».**

**L1-06 est Terminé (22/10/2026)** et **L1-11 est Terminé (26/10/2026)** sur la base des essais réels HA rapportés par l’utilisateur. Les validations L3-06 et L3-07 restent acquises. L3-08 a été qualifié le 24/10 : cache/frontend fonctionnel et droits existants constatés, sans modification des permissions.

1. **L3-10 : terminé le 28/10/2026.** Les six familles retenues ont été validées en HA, dernière en date : Exceptions de calendrier (tous les tests convenus OK). La duplication des Moments planifiés demeure exclue et son bouton supprimé avec confirmation HA. Ne pas confondre validation fonctionnelle et nouvelle publication.
2. **L3-12 : reporté.** Étude d'impact du 24/10 conservée ; attribution des droits de gestion aux utilisateurs nommés et lecture seule pour les autres à rediscuter une fois les autres fonctionnalités finalisées. Ne pas changer les droits actuels.
3. **L6-03 et L6-04 terminés le 29/10.** Non-régression frontend validée ; Black, isort profil black et flake8 conformes ; suite Python locale à 449 tests réussis et 100 % de couverture ; les quatre workflows GitHub Actions (`Lint & Formatting`, `HACS Validate`, `Validate with hassfest`, `Run Tests`) confirmés OK par l’utilisateur.
4. **L6-07 — en cours, scénario 1 validé le 29/10.** Installation neuve réussie sur HAOS vierge de Day Planner, tous résultats attendus confirmés par l’utilisateur (intégration, panneau, données initialement vides, entités, stockage, logs, persistance d’un Moment après redémarrage). **Prochain essai : mise à jour sur HAOS isolé** de la base 0.2.2 vers le dépôt courant (manifest 0.2.3 et correctifs L6-03), avec objets de test préexistants. Puis retrait avec/sans suppression de données. Pas d’essai destructif en production.
5. **L6-08 :** préparer ensuite le périmètre, les limites connues et les notes de publication, sans présumer d’une nouvelle release.
6. **L3-11 et L2-02 :** conserver respectivement la création guidée des moments et l'éventuel affichage des métadonnées dans les écrans, sans les confondre avec L3-10.
7. **Nouveau lot 7 — reporté à très long terme (07/11).** Conserver l’export XLSX eedomus v5.16 à sept onglets tel quel. Plus tard, enrichir en priorité les **propriétés du classeur lui-même** (L7-01), puis éventuellement revoir les onglets (L7-02) ; tests et qualification (L7-03). Cela ne modifie pas les priorités actives des lots 1 à 6.

Les validations manuelles d’octobre, dont L6-03 le 29/10, ne comptaient pas comme de nouveaux tests automatisés. **Une nouvelle exécution complète Python a ensuite été communiquée par l’utilisateur le 29/10 : 449 tests réussis, 2 154 instructions, 100 % de couverture. Les quatre workflows CI ont ensuite été confirmés OK le même jour.**

Les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. L3-10 est clôturé, mais les tâches reportées ou à planifier du lot 3 et la qualification finale du lot 6 restent distinctes.

Le ZIP de travail fourni le 28/10 contient un `manifest.json` en **0.2.3** ; la dernière publication explicitement confirmée dans le suivi historique était **0.2.0**, sans vérification de publication plus récente. L’audit métier est implémenté et validé **après la publication 0.2.0**, sans être déclaré livré dans cette dernière. Le lot Metadata reste ouvert pour l’éventuel affichage détaillé ; horaires avancés et calendrier externe conservent leurs statuts. L’i18n reste non prioritaire ; les traductions existantes sont conservées.

