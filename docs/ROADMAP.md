# Day Planner — Roadmap et suivi d’avancement

**Mise à jour : 26 octobre 2026. Version publiée de référence : 0.2.0, dernière version confirmée par l’utilisateur. Traçabilité `Audit` intégrée ; L1-06 (sept essais réels) et L1-11 (absence de rattrapage après arrêt) clôturés. L3-06 et L3-07 validés, et L3-08 qualifié : cache frontend OK, accès complet des non-administrateurs constaté, gestion fine des droits reportée (L3-12). Prochain chantier : L3-10, duplication globale, non encore implémentée. Il ne s’agit pas d’une nouvelle publication.**

La roadmap reprend les **six lots de la première version**. Les sept étapes de finalisation des vues sont rattachées aux lots concernés, avec leurs statuts conservés. Les numéros des lots sont des repères stables ; les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. Les sept essais fonctionnels prévus pour L1-06 sont validés le 22 octobre ; L3-06 est clôturé le 23 octobre après validation des contrôles d’erreurs et d’annulation ; L3-07 est clôturé le 24 octobre après les validations sur ordinateur et mobile. L3-08 a été qualifié le 24 octobre : chargement des fichiers frontend avec rechargement simple après mise à jour/redémarrage et droits CRUD des non-administrateurs constatés. La délégation fine des droits reste volontairement reportée à L3-12. L1-11 a été validé en conditions réelles le 26 octobre ; L3-10 (duplication) devient le prochain chantier.

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

**Dernier rapport complet chiffré communiqué par l’utilisateur le 21 octobre 2026 : 449 tests, 2 146 instructions mesurées, 0 non couverte, 100 % de couverture Python, 5 avertissements, 1,67 s, Python 3.14.3.** Les tests et validations fonctionnelles ultérieurs ont été confirmés sans nouveau comptage complet publié. Le 20 octobre, le retour à 100 % après compléments `action_executor.py` et `logbook.py` avait déjà été confirmé. **Résultat historique du 14 octobre :** 407 tests réussis, 1 908 instructions mesurées, aucune non couverte, 100 % de couverture Python, 5 avertissements, 1,22 s, Python 3.14.3. Ces résultats ne sont pas des exécutions de la suite complète par l'assistant. Aucun seuil bloquant de couverture n'est souhaité.

**Résultat historique du 13 octobre :** le README des tests annonce **394 tests réussis, 1 877 lignes mesurées et 100 % de couverture**, au **13 octobre 2026 à 15:28:05 Europe/Paris**. La relecture a vérifié la cohérence de ce tableau et les générateurs de rapports avec des données synthétiques ; elle n'a pas réexécuté la suite complète.

## 3. Vue d’ensemble des lots

| Lot | Intitulé | Version cible indicative | Avancement actuel |
| --- | --- | --- | --- |
| 1 | Stabiliser le socle | Corrections livrées en 0.2.0 | Corrections fonctionnelles, workflow et versions/changelog terminés ; L1-06 validé le 22/10 et L1-11 validé le 26/10 après arrêt couvrant un événement. |
| 2 | Intégrer les Metadata / `Audit` | À définir après 0.2.0 | Modèles, moteur, persistance et trois interfaces validés ; présentation détaillée des métadonnées dans l’interface restant à qualifier. |
| 3 | Simplifier la gestion quotidienne | 0.3.0 | En cours ; les cinq vues sont validées. Formulaires (L3-06), clavier/mobile (L3-07) validés ; L3-08 qualifié (cache OK, permissions existantes constatées). Attribution fine des droits reportée (L3-12). Duplication globale (L3-10) prioritaire, non encore implémentée. |
| 4 | Ajouter les horaires avancés | 0.4.0 | À planifier ; périmètre à préciser. |
| 5 | Ajouter une source de calendrier externe | 0.5.0 | À planifier ; règles de synchronisation à définir. |
| 6 | Qualifier la première version stable | 1.0.0 | À préparer après consolidation du périmètre retenu. |

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
| L3-10 | 3 | Dupliquer tous les objets gérés en complément de modifier/supprimer | À planifier | Ajouter une action « Dupliquer » aux Moments, Actions, Types de journée, Moments planifiés, Semaines types, Cycles et Exceptions ; formulaire prérempli, nouvel ID, validation des contraintes, nouvel audit et tests. | Extension demandée par l’utilisateur le 22/10 ; aucune implémentation ni validation encore annoncée. | 22/10/2026 |
| L3-11 | 3 | Ajout guidé des moments prédéfinis | À planifier | Conserver comme amélioration future indépendante de L3-10 ; en préciser le parcours après consolidation. | Sous-sujet préexistant à L3-10, conservé lors de sa scission le 22/10/2026. | 22/10/2026 |
| L3-12 | 3 | Gestion déléguée des droits (gestionnaires/lecteurs) | Reporté | Réexaminer après finalisation des autres fonctionnalités : délégation par utilisateur, droit de modifier les actions HA, protection API/WebSocket et services. | Étude d’impact du 24/10, décision utilisateur le même jour de reporter l’évolution sans changer les droits actuels. | 24/10/2026 |
| L4-01 | 4 | Horaires avancés | À planifier | Définir règles, indisponibilités, passages de date et compatibilité. | Évolution conservée. | 13/10/2026 |
| L5-01 | 5 | Source de calendrier externe | À planifier | Définir source, correspondances, priorités et synchronisation. | Évolution conservée. | 13/10/2026 |
| L6-01 | 6 | Résultat de couverture de référence | Terminé | Actualiser après chaque exécution pertinente ; conserver les résultats précédents dans l’historique. | 21/10 : 449 tests, 2 146 instructions, 0 non couverte, 100 %, 5 avertissements, 1,67 s, Python 3.14.3. Historique 14/10 conservé dans le journal et les guides. | 22/10/2026 |
| L6-02 | 6 | Validation backend et WebSocket/API après corrections | Terminé | Relancer après de nouvelles modifications ; L1-06 validé le 22/10 et L1-11 validé séparément le 26/10. | Suite complète réussie selon le résultat utilisateur : 407 tests après ajout des tests de minuit et des changements d'heure. | 14/10/2026 |
| L6-03 | 6 | Tests ciblés frontend et essais visuels | En cours | Compléter les contrôles visuels et interactions utiles sur panneau/carte et ordinateur/mobile ; confirmer les conditions d’erreur et d’attente si nécessaire. | Essais fonctionnels HA des cinq vues confirmés ; simulations API sur version précédente et contrôle syntaxique/relecture des six corrections du dernier fichier. | 19/10/2026 |
| L6-04 | 6 | HACS et lint/format | À faire | Exécuter les contrôles du périmètre livré. | Résultats restant à confirmer. | 13/10/2026 |
| L6-05 | 6 | Documentation actualisée dans le dépôt | Terminé | Corriger ensuite les constats devenus obsolètes et le texte sur les plugins. | Documentation intégrée dans le ZIP relu. | 13/10/2026 |
| L6-06 | 6 | Cohérence finale de la documentation | Terminé | Intégrer les fichiers actualisés au dépôt ; maintenir les guides au fil des prochaines évolutions. | Documentation alignée sur 0.2.0, résultat GitHub Actions du 14/10 à 12:15:34, L1-07/L1-09 terminés, L1-06 alors en cours (état historique du 14/10) ; fichiers préparés pour intégration. | 14/10/2026 |
| L6-07 | 6 | Installation, mise à jour et retrait | À faire | Vérifier installation neuve, migrations et retrait avec/sans suppression. | Qualification prévue. | 13/10/2026 |
| L6-08 | 6 | Préparation d'une version propre | À faire | Fixer périmètre, notes de release et limites connues. | Qualification prévue. | 13/10/2026 |
| L6-09 | 6 | Tests de régression de l’exécution et du Journal de bord | Terminé | Maintenir les nouveaux cas lors des évolutions de scripts et des mises à jour HA. | 20/10 : 19 tests ciblés réussis en simulation, modules `action_executor.py` et `logbook.py` à 100 % ciblés ; couverture globale 100 % confirmée ensuite par l’utilisateur. | 20/10/2026 |

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
- Vérifier HACS, lint et formatage.
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

**Statut : prochain chantier après L1-11 (26 octobre 2026), sans implémentation à ce jour.** Ajout demandé le 22 octobre 2026. Cette fonctionnalité complète les commandes de gestion existantes (« Éditer/Modifier » et « Supprimer ») sans rouvrir les validations déjà acquises ni considérer la duplication comme implémentée.

#### Périmètre de l'action « Dupliquer »

- **Moments :** créer un nouveau moment à partir d'un existant ; reprendre son nom, son icône et ses actions. Générer de nouveaux identifiants pour le moment et pour les actions copiées. Les références des journées vers le moment source restent inchangées.
- **Actions d'un moment :** dupliquer une action (libellé et séquence Home Assistant) dans le même moment, avec un identifiant d'action distinct ; aucune exécution lors de la copie.
- **Types de journée :** reprendre les horaires et les moments planifiés dans un nouveau type de journée ; copier les entrées enfants avec de nouveaux identifiants si nécessaire, tout en conservant les références vers les moments existants.
- **Moments planifiés :** dupliquer une affectation moment/horaire dans un type de journée, sans contourner les contraintes de validation et d'unicité applicables.
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

Les sept familles d'objets sont duplicables depuis leur gestion, avec des identifiants valides, sans modifier la source, avec un nouvel audit ; les cas de limites, erreurs API, annulation, dépendances et rafraîchissement sont testés. Les éléments de structure réutilisables restent des références ; les contenus enfants propres à une copie sont indépendants.

### Améliorations ultérieures conservées

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
- Vérifier HACS, lint et formatage.
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

## 11. Mise à jour du suivi et journal conservé

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

## 12. Prochaine étape

**L1-06 est Terminé (22/10/2026)** et **L1-11 est Terminé (26/10/2026)** sur la base des essais réels HA rapportés par l’utilisateur. Les validations L3-06 et L3-07 restent acquises. L3-08 a été qualifié le 24/10 : cache/frontend fonctionnel et droits existants constatés, sans modification des permissions.

1. **L3-10 : priorité suivante, duplication des objets.** Commencer par les Moments puis les Actions, et avancer fichier par fichier. Conserver le même parcours d'ajout, avec formulaire prérempli, nouvel identifiant, nouvel audit et aucune modification de la source. Tester chaque étape avant la suivante.
2. **L3-12 : reporté.** Étude d'impact du 24/10 conservée ; attribution des droits de gestion aux utilisateurs nommés et lecture seule pour les autres à rediscuter une fois les autres fonctionnalités finalisées. Ne pas changer les droits actuels.
3. **L6-03 / L6-04 :** maintenir les contrôles des formulaires/clavier/mobile, puis confirmer HACS et lint/format avant la livraison.
4. **L3-11 et L2-02 :** conserver respectivement la création guidée des moments et l'éventuel affichage des métadonnées dans les écrans, sans les confondre avec L3-10.

Les validations manuelles du 26/10 n’impliquent aucun nouveau comptage de tests Python ; la dernière suite complète chiffrée connue demeure le résultat utilisateur du 21/10.

Les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. Cela ne clôture ni tout le lot 3, ni la qualification finale du lot 6.

La version publiée de référence reste 0.2.0, dernière version confirmée. L’audit métier est implémenté et validé **après cette publication**, sans être déclaré livré dans 0.2.0. Le lot Metadata reste ouvert pour l’éventuel affichage détaillé ; horaires avancés et calendrier externe conservent leurs statuts. L’i18n reste non prioritaire ; les traductions existantes sont conservées.

