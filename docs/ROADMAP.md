# Day Planner — Roadmap

**Base : version 0.1.0, ZIP relu le 12 octobre 2026.**

Les versions ci-dessous sont des cibles proposées, pas des engagements de publication. Les lots sont ordonnés par dépendance et par impact sur la fiabilité du planning. Aucune date n'est fixée avant validation du périmètre et des résultats de chaque lot.

## 1. Objectif

Disposer d'un agenda Home Assistant fiable et simple à gérer : moments réutilisables, horaires dans les types de journée, types de semaine, cycles et exceptions dans le calendrier.

Le projet conserve une seule configuration et un seul profil. La logique métier reste séparée des interfaces Home Assistant. Les nouvelles vérifications sont ajoutées dans les fichiers de tests existants correspondant aux modules concernés.

## 2. Point de départ

### Présent dans les sources 0.1.0

- Gestion des moments, actions, types de journée, moments planifiés, types de semaine, cycles et exceptions.
- Résolution du type de journée et calcul des événements.
- Planification Home Assistant et exécution des séquences d'actions.
- Stockage persistant.
- Trois capteurs et un calendrier Home Assistant.
- Panneau de gestion, carte Lovelace, services et API WebSocket.
- Horaires fixes.

La documentation mise à jour est préparée ; son intégration au dépôt reste à effectuer.

### Écarts établis par la relecture

- Versions incohérentes entre `const.py` et `manifest.json`.
- Vérifications CI héritées d'eedomus et échec pytest masqué.
- Dépendance de couverture absente de `requirements-dev.txt`.
- Contrôle incomplet des références des sept jours d'un type de semaine.
- Classe `Audit` présente mais non intégrée aux objets persistés.
- Deux entrées 0.1.0 dans le changelog.

Le ZIP contient 18 fichiers de tests et 365 fonctions de test, hors expansion des paramétrages. Leur réussite et leur couverture n'ont pas été mesurées pendant la relecture.

## 3. Vue d'ensemble

| Ordre | Lot | Version cible proposée | Résultat attendu | Dépendance |
| --- | --- | --- | --- | --- |
| 1 | Stabiliser le socle | 0.1.1 | CI fiable, configuration cohérente, comportement temporel vérifié. | Base 0.1.0 |
| 2 | Intégrer les Metadata | 0.2.0 | Auteur et horodatage conservés pour les modifications. | Lot 1 |
| 3 | Simplifier la gestion quotidienne | 0.3.0 | Création du planning guidée et erreurs compréhensibles. | Lots 1 et 2 |
| 4 | Ajouter les horaires avancés | 0.4.0 | Horaires fixes et premières règles dynamiques cohérentes. | Lots 1 et 2 ; besoins à préciser |
| 5 | Ajouter une source de calendrier externe | 0.5.0 | Exceptions issues d'un calendrier, avec règles de priorité explicites. | Lots 1 à 3 ; contrat de synchronisation à définir |
| 6 | Qualifier la première version stable | 1.0.0 | Installation, mise à jour et usage quotidien validés. | Lots retenus pour la 1.0 |

Les lots 4 et 5 peuvent être inversés selon le besoin prioritaire. La version 1.0 peut être publiée sans ces deux extensions si le périmètre stable est limité au calendrier interne et aux horaires fixes.

## 4. Lot 1 — Stabiliser le socle

**Priorité : immédiate.**

### 1A. Rendre les résultats de validation fiables

- Retirer du workflow les chemins et vérifications eedomus.
- Faire échouer la CI lorsque pytest échoue ; supprimer le `|| echo` masquant son résultat.
- Déclarer les dépendances nécessaires à la mesure de couverture et aligner les commandes locales et CI.
- Harmoniser les versions exposées par l'intégration.
- Fusionner les entrées 0.1.0 après vérification de la date de publication.
- Intégrer le README et les deux guides actualisés.

### 1B. Compléter l'intégrité de la configuration

- Vérifier les sept références de types de journée de chaque `WeekSchedule`.
- Vérifier les chemins service, WebSocket et Options Flow pour que les mêmes règles métier s'appliquent.
- Présenter clairement les erreurs de référence, de doublon et de suppression d'un objet utilisé.
- Vérifier la validation des séquences d'actions avant sauvegarde ; définir les erreurs attendues.

### 1C. Vérifier les cas temporels sensibles

Ces points sont à contrôler ; ils ne sont pas tous des défauts confirmés :

- Deux moments différents programmés exactement à la même heure : chacun doit être exécuté une fois. La recherche d'un prochain événement strictement futur nécessite une attention particulière à ce cas.
- Passage de minuit : mise à jour du type de journée et du moment courant.
- Redémarrage, rechargement et modification du planning près d'un déclenchement.
- Échec d'une action : poursuite des actions suivantes et maintien de la planification.
- Changement d'heure : définir le comportement pour une heure inexistante ou répétée, puis le tester.
- Rappels annulés et protection contre les exécutions répétées.
- Conservation de la règle actuelle : aucun rattrapage des événements passés.

### Critères de sortie

- Tous les tests passent ; une erreur de test rend la CI rouge.
- La couverture réelle est publiée et l'objectif de 100 % du code Python mesuré est atteint, sans exclusions ajoutées uniquement pour améliorer le chiffre.
- Les nouveaux tests vérifient les comportements et les cas d'échec dans les fichiers existants concernés.
- Un essai Home Assistant confirme les événements simultanés, le passage de minuit et le rechargement.
- Documentation, manifeste et changelog décrivent le même état du projet.

## 5. Lot 2 — Intégrer les Metadata

**Objectif : savoir qui a créé ou modifié chaque objet, et quand.**

### Travaux

- Remplacer le concept `Audit` par `Metadata`, conformément à la terminologie du projet.
- Définir `created_by`, `created_at`, `modified_by`, `modified_at` et une convention d'horodatage cohérente.
- Couvrir les moments, actions, types de journée, moments planifiés, types de semaine, cycles et exceptions.
- Préciser qu'une modification d'un élément imbriqué actualise également les Metadata de son parent.
- Définir l'identité enregistrée pour une modification utilisateur, une automatisation et une opération interne. Ne pas inventer d'auteur lorsque le contexte est absent.
- Centraliser leur mise à jour pour les services, WebSocket et Options Flow.
- Ajouter sérialisation, désérialisation et migration des données 0.1.0. Les objets historiques sans auteur connu restent identifiés comme tels.
- Afficher les informations de modification dans les détails des objets.

### Critères de sortie

- Chaque interface de modification enregistre des Metadata cohérentes.
- Les données de création sont préservées lors d'une modification.
- Une ancienne configuration est migrée sans perdre objets, horaires ni actions.
- Rechargement et redémarrage conservent les Metadata.

## 6. Lot 3 — Simplifier la gestion quotidienne

**Objectif : construire et corriger un planning depuis l'interface avec peu de manipulations.**

### Travaux

- Améliorer l'état vide avec le parcours moments → journées → semaines → cycle.
- Proposer l'ajout explicite des moments prédéfinis, sans écraser les moments existants.
- Ajouter la duplication des types de journée et des types de semaine avec de nouveaux identifiants.
- Montrer les dépendances empêchant une suppression.
- Afficher dans le calendrier le planning d'origine et l'exception appliquée.
- Harmoniser les messages d'erreur et les traductions françaises/anglaises.
- Vérifier le panneau et la carte Lovelace sur ordinateur et mobile.
- Définir puis vérifier les droits de consultation et de modification de la configuration et des actions.

### Critères de sortie

- Un utilisateur crée un premier planning complet depuis le panneau sans modifier le stockage.
- Une exception peut être ajoutée, modifiée et retirée avec un résultat immédiatement visible.
- Les blocages expliquent quel objet est encore utilisé.
- Les permissions et les erreurs sont cohérentes entre les interfaces.

## 7. Lot 4 — Ajouter les horaires avancés

**Périmètre proposé à préciser avant développement : lever/coucher du soleil avec décalage.**

### Travaux

- Faire évoluer `TimeDefinition` pour distinguer heure fixe et règle dynamique, en conservant les horaires existants.
- Définir le résultat lorsqu'un horaire ne peut pas être calculé et lorsqu'un décalage franchit minuit.
- Maintenir le tri, la gestion des événements simultanés et la cohérence entre affichage et exécution.
- Recalculer le planning lorsque les données nécessaires changent.
- Ajouter l'édition des règles dans le panneau et les formulaires concernés.
- Migrer le stockage si nécessaire et actualiser les schémas des services et WebSocket.

### Critères de sortie

- Une même règle produit le même horaire dans le panneau, les entités et l'ordonnanceur.
- Les configurations utilisant seulement `fixed_time` restent compatibles.
- Les cas d'horaire indisponible et de changement de date sont définis, documentés et testés.

## 8. Lot 5 — Ajouter une source de calendrier externe

**Objectif : alimenter les exceptions depuis un calendrier, notamment Google Calendar.**

### Décisions nécessaires avant développement

- Choisir un calendrier exposé par Home Assistant ou un connecteur direct ; privilégier la réutilisation d'une intégration existante si elle couvre le besoin.
- Proposer une première version en lecture seule du calendrier externe.
- Définir comment un événement désigne un type de journée : convention de titre, description ou autre règle explicite.
- Fixer la priorité proposée : exception locale explicite → exception externe reconnue → cycle.
- Définir événements sur plusieurs jours, fuseaux horaires, conflits et indisponibilité de la source.

### Travaux

- Ajouter le choix de la source et les règles de correspondance.
- Conserver l'origine et l'identifiant externe des exceptions importées pour éviter les doublons.
- Répercuter modifications et suppressions externes sans supprimer les exceptions locales.
- Afficher l'origine des exceptions dans le calendrier.
- Définir une stratégie de rafraîchissement et de conservation des dernières données connues.

### Critères de sortie

- Les règles de priorité sont documentées et visibles dans le résultat du planning.
- Un même événement externe ne crée pas plusieurs exceptions lors des synchronisations.
- Une panne de la source externe n'altère pas les données locales.
- La suppression ou la modification d'un événement externe est traitée selon les règles définies.

## 9. Lot 6 — Qualifier la première version stable

### Travaux

- Fixer le périmètre exact de la 1.0 et mettre à jour le statut de chaque lot.
- Vérifier installation neuve, retrait avec/sans suppression et mise à jour depuis la 0.1.0.
- Tester les migrations sur des copies de configurations réalistes.
- Vérifier le rechargement, le fonctionnement sur plusieurs journées et les changements de cycles.
- Réaliser une période d'observation proposée de deux semaines avec un planning représentatif.
- Finaliser guides utilisateur, exemples, dépannage, notes de release et compatibilité déclarée.
- Vérifier les métadonnées et contrôles nécessaires à la distribution HACS retenue.

### Critères de sortie

- Aucun défaut connu provoquant perte de données ou déclenchement incorrect dans le périmètre retenu.
- Validation automatisée réussie et résultats datés disponibles.
- Installation et mise à jour reproductibles avec la documentation livrée.
- Limites restantes explicitement documentées.

## 10. Suivi des lots

Pour chaque lot, suivre : statut, tâches terminées, décisions prises, blocages, résultat des tests et critère de sortie restant. Un lot est validé lorsque ses critères de sortie sont satisfaits, pas uniquement lorsque son code est écrit.

Le point hebdomadaire peut reprendre ces informations en ne signalant que les changements importants.

## 11. Prochaine étape recommandée

Commencer par **le lot 1A : CI, dépendances, versions et documentation**, puis compléter le validateur et vérifier les événements simultanés et les transitions de journée avant d'ajouter les Metadata.

L'import/export, les profils multiples et la synchronisation bidirectionnelle des calendriers restent hors de cette roadmap initiale ; ils pourront être étudiés si un besoin concret apparaît.
