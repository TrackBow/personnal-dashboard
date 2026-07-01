# Personal Dashboard

Un tableau de bord personnel moderne et épuré développé en Python avec **CustomTkinter**. Cet outil regroupe trois fonctionnalités clés pour centraliser la gestion des tâches quotidiennes, la prise de notes et le suivi de la productivité.

## 🚀 Fonctionnalités

* **Tableau de Bord (Accueil) :** Une vue d'ensemble dynamique qui résume le statut de la To-Do List (tâches accomplies/restantes), affiche les notes récentes et présente le temps de focus cumulé de la journée sous forme de cartes cliquables.
* **To-Do List :** * Ajout et suppression rapide de tâches.
    * Gestion des priorités (Haute / Normale) via un menu contextuel (clic droit).
    * Sauvegarde automatique dans un fichier local `tasks.json`.
* **Gestionnaire de Notes :**
    * Création, renommage et suppression de pages de notes indépendantes.
    * Barre de recherche en temps réel pour filtrer les notes.
    * Formatage basique du texte (Gras, Italique, Souligné, Couleur).
    * Sauvegarde automatique toutes les 5 secondes et exportation au format `.txt`.
* **Timer de Focus (Style Pomodoro) :**
    * Timer personnalisable (Minutes/Secondes) avec alternance automatique entre les sessions de Travail et de Pause.
    * Alerte sonore à la fin d'un cycle.
    * Suivi de l'activité via un graphique en barres généré dynamiquement pour visualiser le temps investi sur les 7 derniers jours.
    * Sauvegarde des statistiques dans `stats.json`.

