# RALA_IA

## 1. Vue d'ensemble du projet
L'objectif était de transformer ton intelligence artificielle locale (qwen2.5:0.5b propulsée par Ollama) en un service embarqué prêt à l'emploi sur la Jetson Orin Nano, accessible de deux manières :
•	Via le Web : Une interface graphique de chat moderne (Streamlit) accessible depuis ton PC via l'adresse IP fixe de liaison (192.168.55.1:8501).
•	Via le Terminal (CLI) : Une commande globale simple (ralah cli) depuis une connexion SSH.
•	En mode Automatique : Tout se lance tout seul dès l'allumage (boot) de la Jetson sans aucune intervention humaine.

## 2. Explication globale de chaque script et fichier
### A. Le cœur de l'IA : Ollama & le Modèle
•	Ollama : C'est le moteur d'exécution local qui fait tourner les grands modèles de langage (LLM) directement sur le matériel de la Jetson.
•	Modèle qwen2.5:0.5b : Un modèle léger, rapide et optimisé pour tourner de manière fluide sur les ressources de la carte, tout en gérant très bien le français et la génération de texte.
### B. ralah_web.py (L'interface Web Streamlit)
•	Son rôle : Fournir une interface graphique web interactive de type "chat" (analogue à une application de messagerie ou ChatGPT).
•	Comment il fonctionne : Il utilise le framework Python Streamlit pour dessiner l'interface dans le navigateur. Il intègre également des bibliothèques comme pypdf pour permettre d'importer et d'analyser des documents PDF directement dans la conversation.
•	Commande de lancement manuelle (de base) :
Bash
python3 -m streamlit run ralah_web.py --server.address 0.0.0.0 --server.port 8501
### C. ralah_cli.py (Le mode Terminal Interactif)
•	Son rôle : Permettre de discuter avec l'assistant directement dans un terminal texte (en SSH par exemple).
•	Comment il fonctionne : Il établit une liaison directe avec l'API Python d'Ollama (import ollama) dans une boucle textuelle input(). Il récupère tes messages, les envoie au modèle qwen2.5:0.5b, et affiche la réponse en temps réel dans la console avec une mise en forme stylisée.
### D. La commande globale /usr/local/bin/ralah (Le gestionnaire CLI)
•	Son rôle : Créer une commande système globale nommée ralah utilisable depuis n'importe quel dossier de la machine.
•	Comment il fonctionne : C'est un script Bash positionné dans /usr/local/bin/ralah qui agit comme un aiguilleur (via une structure case "$1" en bash) :
•	Si tu tapes ralah web, il se déplace dans le dossier du projet et lance l'interface Streamlit.
•	Si tu tapes ralah cli, il lance le script terminal ralah_cli.py.
•	Si tu tapes juste ralah, il affiche l'aide.
### E. Le service systemd /etc/systemd/system/ralah.service (L'automatisation au démarrage)
•	Son rôle : Assurer qu'à chaque allumage de la Jetson Orin Nano, l'assistant web démarre tout seul en arrière-plan comme un service système (daemon).
•	Comment il est configuré :
•	After=network.target ollama.service : Il attend que le réseau et Ollama soient complètement chargés avant de démarrer.
•	User=admin-nano : Il s'exécute sous ton profil utilisateur.
•	ExecStart=... --server.headless true : Il lance Streamlit en mode silencieux/arrière-plan.
•	Restart=always : Si l'application plante ou rencontre un souci, le système la relance automatiquement au bout de 5 secondes.

## Bilan de ton installation
Tu disposes désormais d'un système complet, robuste et autonome :
1.	Au boot : Ollama et l'interface Web s'allument en arrière-plan.
2.	Sur le réseau : Tu ouvres ton navigateur sur ton PC Kali (blackhat) à l'adresse [http://192.168.55.1:8501](http://192.168.55.1:8501) et tu discutes avec ton IA.
3.	En SSH : Tu tapes ralah cli pour interagir en mode terminal.

