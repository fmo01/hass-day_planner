# Day Planner — Roadmap et suivi d’avancement

**Mise à jour : 19 octobre 2026. Version publiée de référence : 0.2.0, dernière version confirmée par l’utilisateur. Relecture frontend actualisée avec les fichiers des 19 octobre et corrections validées à 11 h 57.**

La roadmap reprend les **six lots de la première version**. Les sept étapes de finalisation des vues sont rattachées aux lots concernés, avec leurs statuts conservés. Les numéros des lots sont des repères stables ; les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. Le travail immédiat porte sur les contrôles transversaux restants ; L1-06 reste en cours.

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

**Résultat courant communiqué par l'utilisateur le 14 octobre 2026 : 407 tests réussis, 1 908 instructions mesurées, aucune non couverte et 100 % de couverture Python ; 5 avertissements, durée 1,22 s, Python 3.14.3.** Ce résultat valide la suite après correction des moments simultanés, des références des semaines et du calcul des changements d'heure ; le test de passage de minuit est également réussi. Il n'a pas été réexécuté par l'assistant. Aucun seuil bloquant de couverture n'est souhaité.

**Résultat historique du 13 octobre :** le README des tests annonce **394 tests réussis, 1 877 lignes mesurées et 100 % de couverture**, au **13 octobre 2026 à 15:28:05 Europe/Paris**. La relecture a vérifié la cohérence de ce tableau et les générateurs de rapports avec des données synthétiques ; elle n'a pas réexécuté la suite complète.

## 3. Vue d’ensemble des lots

| Lot | Intitulé | Version cible indicative | Avancement actuel |
| --- | --- | --- | --- |
| 1 | Stabiliser le socle | Corrections livrées en 0.2.0 | Corrections fonctionnelles, workflow et versions/changelog terminés. L1-06 reste en cours pour les essais réels HA. |
| 2 | Intégrer les Metadata | À définir après 0.2.0 | À planifier après consolidation des vues. |
| 3 | Simplifier la gestion quotidienne | 0.3.0 | En cours ; les cinq vues sont validées. Corrections transversales de robustesse vérifiées ; accessibilité, responsive, cache et permissions restent à qualifier. |
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
| L1-06 | 1 | Transitions temporelles et rechargement | En cours | Confirmer dans HA les déclenchements, le passage de minuit, les redémarrages/rechargements, l’absence de doublons et de rattrapage après arrêt. Aucun nouveau rappel programmé par cette mise à jour. | Tests Python de minuit et DST réussis ; 407 tests et 100 % communiqués le 14/10. Maintien explicite en cours par l’utilisateur ; essais réels du planificateur non confirmés. | 19/10/2026 |
| L1-07 | 1 | Filtres et présentation du workflow | Terminé | Conserver les rapports et la mise à jour automatique du README, sans seuil bloquant. | Exécution tests.yml réussie confirmée par l'utilisateur ; README généré le 14/10 à 12:15:34 : 407 tests, 1 908 instructions, 100 %. | 14/10/2026 |
| L1-08 | 1 | Seuil de couverture imposé en CI | Abandonné | Ne pas ajouter de seuil bloquant ; conserver la mesure et les rapports de couverture. | Décision explicite de l'utilisateur le 14/10 : refus de --cov-fail-under=100. L'objectif de couverture reste suivi. | 14/10/2026 |
| L1-09 | 1 | Versions et changelog | Terminé | Maintenir le manifeste comme référence ; laisser semantic-release gérer les prochaines versions. | Utilisateur : L1-09 terminé. Manifeste 0.2.0 ; ancienne constante supprimée ; entrée 0.1.0 du 10/10 restaurée d'après le tag et doublons retirés. | 14/10/2026 |
| L2-01 | 2 | Modèle Metadata et règles auteur/horodatage | À planifier | Définir le contrat et remplacer le concept Audit. | Évolution conservée. | 13/10/2026 |
| L2-02 | 2 | Persistance, migration et interfaces Metadata | À planifier | Sérialisation, migration, services, WebSocket, Options Flow et affichage. | Évolution conservée. | 13/10/2026 |
| L3-01 | 3 | Moments | Terminé et figé | Maintenir les tests de non-régression. | Statut utilisateur : CRUD, groupes d'actions, détails, traduction HA, i18n, comptages, erreurs. | 13/10/2026 |
| L3-02 | 3 | Types de journée | Terminé | Maintenir les comportements validés ; aucun nouveau travail fonctionnel prévu sur cette vue. | Essais utilisateur HA : CRUD, dépendances et conservation des saisies de création, renommage et moments planifiés. Boutons et gardes relus. | 19/10/2026 |
| L3-03 | 3 | Semaines types | Terminé | Maintenir les sept affectations, la conservation des saisies et les messages dans les dialogues. | Quatre essais HA confirmés : création invalide, modification invalide, CRUD et suppression refusée si utilisée par un cycle ; visibilité des erreurs validée. | 19/10/2026 |
| L3-04 | 3 | Cycles | Terminé | Maintenir le CRUD, les brouillons, les messages i18n et les protections relues ; comportement temporel réel suivi dans L1-06. | Essais HA des cycles tous confirmés le 18/10 ; corrections complémentaires de robustesse relues le 19/10 dans le dernier fichier syntaxiquement valide. | 19/10/2026 |
| L3-05 | 3 | Calendrier / Exceptions | Terminé | Maintenir le remplacement du programme par une exception et le retour au cycle après suppression ; L1-06 reste distinct. | Tous les essais HA confirmés le 19/10 : CRUD, description facultative vide, conservation des saisies, type appliqué et retour au programme après suppression. | 19/10/2026 |
| L3-06 | 3 | Cohérence transversale des modales et messages | En cours | Terminer le contrôle global des ouvertures/fermetures, annulations et erreurs, notamment lors d’un échec API ; ne pas confondre relecture et essais HA. | Corrections relues le 19/10 : protection de l’édition cycle lors des actualisations HA, gardes et boutons cycles/exceptions, render dans finally et ordre des validations. | 19/10/2026 |
| L3-07 | 3 | Nettoyage CSS/JS, accessibilité et responsive | En cours | Poursuivre le nettoyage ciblé ; vérifier focus, clavier, libellés et petits écrans sans rouvrir les moments figés sans défaut concret. | 14 fichiers frontend relus : 12 JS et 2 JSON syntaxiquement valides ; gestionnaire de suppression cycle en double retiré et vérifié. | 19/10/2026 |
| L3-08 | 3 | Cache/versioning frontend et permissions | À faire | Vérifier chargement après mise à jour et droits retenus. | Passage transversal prévu. | 13/10/2026 |
| L3-09 | 3 | i18n restante | Reporté | Traiter opportunément lorsqu'un composant est retouché ; ne bloque pas un lot. | Priorité utilisateur. | 13/10/2026 |
| L3-10 | 3 | Duplication et moments prédéfinis guidés | À planifier | Sélectionner selon les besoins après consolidation. | Améliorations conservées. | 13/10/2026 |
| L4-01 | 4 | Horaires avancés | À planifier | Définir règles, indisponibilités, passages de date et compatibilité. | Évolution conservée. | 13/10/2026 |
| L5-01 | 5 | Source de calendrier externe | À planifier | Définir source, correspondances, priorités et synchronisation. | Évolution conservée. | 13/10/2026 |
| L6-01 | 6 | Résultat de couverture de référence | Terminé | Actualiser après chaque exécution pertinente ; conserver les résultats précédents dans l'historique. | Résultat utilisateur du 14/10 : 407 tests réussis, 1 908 instructions, 0 non couverte, 100 %, 5 avertissements, 1,22 s ; Python 3.14.3. | 14/10/2026 |
| L6-02 | 6 | Validation backend et WebSocket/API après corrections | Terminé | Relancer après de nouvelles modifications ; la validation réelle HA de L1-06 reste ouverte. | Suite complète réussie selon le résultat utilisateur : 407 tests après ajout des tests de minuit et des changements d'heure. | 14/10/2026 |
| L6-03 | 6 | Tests ciblés frontend et essais visuels | En cours | Compléter les contrôles visuels et interactions utiles sur panneau/carte et ordinateur/mobile ; confirmer les conditions d’erreur et d’attente si nécessaire. | Essais fonctionnels HA des cinq vues confirmés ; simulations API sur version précédente et contrôle syntaxique/relecture des six corrections du dernier fichier. | 19/10/2026 |
| L6-04 | 6 | HACS et lint/format | À faire | Exécuter les contrôles du périmètre livré. | Résultats restant à confirmer. | 13/10/2026 |
| L6-05 | 6 | Documentation actualisée dans le dépôt | Terminé | Corriger ensuite les constats devenus obsolètes et le texte sur les plugins. | Documentation intégrée dans le ZIP relu. | 13/10/2026 |
| L6-06 | 6 | Cohérence finale de la documentation | Terminé | Intégrer les fichiers actualisés au dépôt ; maintenir les guides au fil des prochaines évolutions. | Documentation alignée sur 0.2.0, résultat GitHub Actions du 14/10 à 12:15:34, L1-07/L1-09 terminés, L1-06 toujours en cours ; fichiers préparés pour intégration. | 14/10/2026 |
| L6-07 | 6 | Installation, mise à jour et retrait | À faire | Vérifier installation neuve, migrations et retrait avec/sans suppression. | Qualification prévue. | 13/10/2026 |
| L6-08 | 6 | Préparation d'une version propre | À faire | Fixer périmètre, notes de release et limites connues. | Qualification prévue. | 13/10/2026 |

## 5. Lot 1 — Stabiliser le socle

**Statut : partiellement réalisé.** Les corrections déjà intégrées restent enregistrées dans le tableau.

### Intégrité et comportement temporel

- **Terminé le 14/10/2026 :** contrôle des sept références des semaines types et tests des journées inconnues. La finalisation de la vue reste suivie dans le lot 3.


- Exécuter les tests backend existants et les tests WebSocket/API.
- Compléter les fichiers existants pour les corrections apportées.
- Ajouter des tests frontend ciblés si les interactions modifiées le justifient, puis effectuer les essais visuels nécessaires.
- **Terminé le 14/10/2026 :** correction et tests des moments simultanés ; tous les moments d'un même horaire sont traités par le rappel. Conserver les tests de non-régression, sans rouvrir la vue Moments.
- Vérifier le passage de minuit, les changements de cycles, le redémarrage et le rechargement près d'un déclenchement.
- Vérifier les erreurs d'actions, les rappels annulés et l'absence de rattrapage des événements passés.
- **Tests Python terminés le 14/10/2026 :** règle de type cron Debian pour les horaires fixes. Au printemps, les occurrences de l'heure supprimée sont regroupées au premier instant valide (03:00 en Europe/Paris) ; en automne, exécution au premier passage seulement. Les essais réels HA restent à confirmer.

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

**Statut : à planifier après consolidation des vues.**


Remplacer le concept `Audit` par `Metadata` et intégrer auteur/date de création et modification aux objets persistés. Centraliser la mise à jour entre services, WebSocket et Options Flow, préserver l'origine de création et migrer les données anciennes sans inventer leur auteur. Les changements d'éléments imbriqués doivent être pris en compte.

Validation attendue : traçabilité cohérente, migration sans perte et persistance après redémarrage. Cette évolution ne précède plus la finalisation des vues de gestion.

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

La description reste facultative ; une chaîne vide est transmise à l’API. Les brouillons conservent les saisies après erreur. Création, modification, effacement de description et suppression avec retour au cycle sont validés. Les travaux ci-dessous restent le périmètre de référence ; la qualification transversale et L1-06 restent ouvertes.

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

**Statut : en cours.** Première série de six corrections terminée et vérifiée sur le dernier fichier le 19 octobre : protection de l’édition cycle lors des actualisations HA, gardes des cinq opérations restantes, désactivation des boutons cycles, rendu final des exceptions, gestionnaire de suppression cycle unique et ordre des validations de date. Les contrôles syntaxiques passent. Aucun nouveau résultat de suite Python ni essai complet clavier/mobile/cache/permissions n’est déduit de cette relecture.

#### Travaux

- Recenser les onglets en français en dur et les messages généraux : « Chargement… », erreurs globales et navigation. Traduire lorsque les composants sont déjà retouchés ; ne pas en faire une condition de sortie.
- Réduire les doublons CSS/JS identifiés sans rouvrir inutilement les vues figées.
- Vérifier la cohérence des modales : ouverture, fermeture, confirmation, annulation et erreurs.
- Vérifier l'accessibilité : focus, navigation clavier, libellés et boutons.
- Vérifier le panneau et la carte Lovelace sur ordinateur et mobile.
- Définir et vérifier le cache/versioning frontend pour qu'une mise à jour charge les nouveaux fichiers.
- Vérifier les droits de consultation et de modification selon le périmètre retenu.

#### Critère de sortie

Les vues ont des comportements communs cohérents et restent accessibles. La mise à jour du frontend ne laisse pas un ancien code en cache dans les scénarios vérifiés. Les écarts i18n non traités restent recensés.

### Améliorations ultérieures conservées

La duplication des journées/semaines et l'ajout guidé des moments prédéfinis restent des améliorations possibles, à sélectionner selon les besoins après consolidation. Import/export, profils multiples et synchronisation bidirectionnelle ne font pas partie du périmètre immédiat.


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
- Vérifier le passage de minuit, les changements de cycles, le redémarrage et le rechargement près d'un déclenchement.
- Vérifier les erreurs d'actions, les rappels annulés et l'absence de rattrapage des événements passés.
- **Tests Python terminés le 14/10/2026 :** règle de type cron Debian pour les horaires fixes. Au printemps, les occurrences de l'heure supprimée sont regroupées au premier instant valide (03:00 en Europe/Paris) ; en automne, exécution au premier passage seulement. Les essais réels HA restent à confirmer.


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

## 12. Prochaine étape

**Terminer le passage transversal final**, en conservant les validations fonctionnelles acquises :

1. L3-06 : contrôler les annulations et les erreurs API dans les dialogues ; confirmer les protections en situation réelle si nécessaire.
2. L3-07 et L6-03 : qualifier clavier, focus et petits écrans, puis panneau et carte Lovelace.
3. L3-08 : vérifier le chargement des nouveaux fichiers après mise à jour et les droits de consultation/modification.
4. L6-04 : confirmer les contrôles HACS et lint/format ; actualiser les documents concernés lors de la livraison.

**L1-06 reste En cours** : essais réels de déclenchement, passage de minuit, redémarrage/rechargement et absence de doublons ou de rattrapage des événements passés. Les rappels historiques restent dans le journal ; aucune échéance future n’est affirmée sans vérification de leur état.

Les vues Moments, Types de journée, Semaines types, Cycles et Calendrier / Exceptions sont validées. Cela ne clôture ni tout le lot 3, ni la qualification finale du lot 6.

La version publiée de référence reste 0.2.0, dernière version confirmée. Metadata, horaires avancés et calendrier externe conservent leurs statuts. L’i18n reste non prioritaire ; les traductions existantes sont conservées.

