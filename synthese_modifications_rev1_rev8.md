# Synthèse des modifications — VP Factory
## Historique complet Rev1 → Rev8

**Fichier stable actuel : `VP_Factory_V9_Rev8.html`**

---

## Rev1 — KPIs Responsable Opérations
- Système de jalons (`milestone`) sur les tâches : Installation / MES / PV Final, affectation automatique par mapping catégorie + affectation manuelle via select dans l'édition de tâche
- **Bloc A — Écarts planning** : 3 KPIs (Installation, MES, PV Final) avec objectifs éditables en live, cartes globales + détail par chargé d'affaires
- **Bloc B — Réserves** : nombre moyen de réserves à la signature du PV + temps moyen de levée
- Visible uniquement en vue Responsable Opérations (Vincent), pas côté CA ni Manager installation

## Rev2 — Module Réserves (OPL) complet
- **Objectif ajustable sur le nombre de réserves** dans le Bloc A, coloration vert/rouge
- **Onglet "Réserves (OPL)"** dans le détail projet, calqué sur le tableau AGO fourni :
  - Création de la liste conditionnée à la signature du PV final
  - 5 statuts : ○ Nouveau · ◔ 25% · ◑ 75% · ◕ Observation · ● Levée
  - Suivi horodaté automatique des changements de statut/échéance
  - Ajout, modification, suppression de réserves

## Rev3 — Planning ressources + démo peuplée
- Correction du champ `group_type` (mismatch bloquant l'affichage des ressources)
- 20 techniciens démo (10 mécaniciens, 10 automaticiens) avec planning réaliste
- KPIs jalons + OPL ajoutés à la fiche de synthèse de clôture projet
- Export PDF de l'OPL, mise en page façon tableau client (bandeau rouge, symboles de statut)

## Rev4 — Toggle Démo / Production
- Fusion des **28 projets réels** (extraits du fichier de travail de Yoann) dans le moteur multi-dashboards
- Deux modes : **Démo** (données fictives, éphémères) et **Production** (vraies données, persistées en localStorage)
- Ajout du bouton "+ Ressource" pour créer ses propres techniciens en production

## Rev5 — Correctifs et cascade de dates
- **Bug critique corrigé** : le démarrage de l'application s'exécutait avant la définition de certaines fonctions (ordre des balises `<script>`), causant un plantage silencieux qui empêchait tout affichage
- Bouton de bascule Démo/Production déplacé en bas à gauche, format interrupteur simple
- **Modale d'édition de tâche enrichie** : champ Durée synchronisé avec Début/Fin, sélecteur de dépendance avec décalage en jours
- **Cascade automatique des dates** : modifier une tâche recalcule automatiquement toutes les tâches qui en dépendent (fonction `propagateDeps`, déjà présente mais jamais branchée — corrigé)

## Rev6 — Gantt Style C unifié
- Nouvelle charte graphique commune : barres en pilule colorées par catégorie, toggle Semaine/Mois en segmented control
- Mode Mois : cases-semaines individuelles visibles, regroupées sous un en-tête par mois
- Appliqué au Gantt détail projet et au planning ressources
- Export PNG existant conservé et re-testé fonctionnel

## Rev7 — Durcissement de la sauvegarde (suite à la perte du journal de bord)
- **Cause de la perte identifiée** : le champ `journal` n'était pas initialisé par défaut sur les projets réels, et un échec silencieux de lecture localStorage provoquait une réinitialisation invisible vers les données d'origine (sans journal)
- Toute erreur d'enregistrement affiche désormais un **bandeau d'alerte visible et persistant** (fini le silence)
- **Copie de secours miroir** : une deuxième copie des projets est maintenue ; si la copie principale est corrompue, récupération automatique depuis le miroir
- Si les deux copies sont perdues, l'app n'écrase plus jamais silencieusement avec des données vides — elle alerte et propose le téléchargement de la donnée brute pour tentative de récupération

## Rev8 — Récupération du journal de bord perdu
- Comparaison de deux sauvegardes (6 et 9 juillet) : confirmation que les 29 projets réels avaient été renumérotés silencieusement, provoquant la perte du journal
- Correspondance par **référence numérique de projet** (stable malgré les changements de nom et d'ID) entre les deux sauvegardes
- **20 entrées de journal restaurées sur 10 projets**, réinjectées dans la base la plus à jour (9 juillet)
- Passage de 28 à **29 projets réels** (un projet manquant dans l'extraction initiale a été retrouvé)
- Marqueur de version ajouté pour forcer le remplacement des données obsolètes en mémoire navigateur, une seule fois, sans perturber la persistance normale ensuite

---

## État actuel du fichier

| Fonctionnalité | État |
|---|---|
| Dashboards par rôle (CA / Responsable Opérations / Manager installation) | ✅ |
| KPIs jalons + réserves, objectifs éditables | ✅ |
| Onglet Réserves (OPL) : création, suivi horodaté, export PDF | ✅ |
| Planning ressources : techniciens, réservations, création libre | ✅ |
| Toggle Démo / Production | ✅ |
| Gantt Style C unifié (projet + ressources), export PNG | ✅ |
| Cascade automatique des dates dépendantes | ✅ |
| Sauvegarde durcie (alertes visibles, copie miroir, jamais de perte silencieuse) | ✅ |
| 29 projets réels avec journal de bord restauré | ✅ |
| Vue d'ensemble multi-projets (timeline globale) | ❌ Pas encore construite — reste un mockup |
| Fusion du module d'alertes riche (vpBuildAlerts) | ❌ En attente de comparaison |
| Cadrage documentaire (cycle de vie projet / services) | ❌ Toujours en attente |

---

## Fichiers de la session
- **`VP_Factory_V9_Rev8.html`** — version stable actuelle
- `synthese_modifications_rev1_rev8.md` — ce document
