# Arcade Skill

[中文](intro.zh.md) · [English](intro.en.md) · [Français](intro.fr.md) · [Italiano](intro.it.md) · [العربية](intro.ar.md)

## Phrase courte

Arcade Skill lance de petits jeux d’arcade nostalgiques dans le navigateur pendant que Claude Code, Codex ou un autre agent de développement compile, teste ou réfléchit très fort.

## Description courte

Arcade Skill est un lanceur de mini-jeux pensé pour les temps morts du développement assisté par IA. Installez le skill une seule fois, puis demandez à jouer pendant que votre agent installe des dépendances, exécute des tests ou génère du code. Le chargeur Python récupère un manifest distant, vérifie le hash sha256 du bundle HTML autonome, le met en cache localement et ouvre le jeu dans le navigateur. L’ambiance est à moitié outil de terminal, à moitié borne d’arcade du vieux web.

## Description longue

Les agents de programmation créent de nouveaux moments d’attente : tests en cours, dépendances en installation, refactorisation automatique, build ou déploiement. Arcade Skill transforme ces pauses en petit jouet de développeur : URL locale, log de manifest, bundle vérifié, et une partie qui démarre avant que vous n’ouvriez machinalement un autre onglet.

Le premier jeu est une réécriture originale de **Down 100 Floors** : se déplacer à gauche ou à droite, tomber de plateforme en plateforme, éviter les pièges et battre son record. Le skill installé reste minimal ; le contenu des jeux est distribué via un manifest distant sur `arcade.fxpeek.com`, ce qui permet d’ajouter des jeux, de modifier les annonces ou de couper une version problématique sans réinstallation.

## Contexte du jeu et règles

**Down 100 Floors** s’inscrit dans la lignée des anciens jeux d’arcade web, Flash et mobile : il ne faut pas monter, mais descendre pour survivre. Les plateformes remontent, le plafond se rapproche, et le joueur doit se déplacer à gauche ou à droite pour atterrir sur la prochaine plateforme.

Le défi est simple : **survivre plus longtemps, descendre plus bas, obtenir un meilleur classement**. Les plateformes normales permettent de reprendre le rythme et de récupérer de la vie. Les pics infligent des dégâts. Les ressorts propulsent le joueur. Les plateformes mobiles ou fragiles perturbent la trajectoire.

Ce type de jeu fonctionne parce qu’une partie est courte et donne immédiatement envie de recommencer. Il convient donc très bien aux petites pauses pendant qu’un agent IA exécute des tests, installe des dépendances ou génère du code. Cette version conserve la boucle nostalgique, mais utilise un code original et des visuels pixel créés pour le projet.

## Classement et équité

La version actuelle conserve le meilleur score local. Lorsqu’un classement global sera ajouté, le mode classé devra rester équitable : mêmes points de vie, aucun bonus payant, aucune résurrection payante, aucune mécanique qui donne un avantage compétitif.

- Classement principal : profondeur maximale atteinte.
- Égalité : le temps le plus court l’emporte.
- Anti-triche : envoyer la version, le mode, la graine aléatoire et un résumé d’événements.
- Partage : le score copié contient `?ref=share` pour mesurer la propagation.
