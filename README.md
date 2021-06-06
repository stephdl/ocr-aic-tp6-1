# ocr-aic-tp6
Auteur 	: 	Pierre LEMAIRE
Version	:	0.1
Date	:	2021-05-17

Travail effectué dans le cadre de la formation Administrateur Infrastructure et Cloud 
d'OpenClassrooms, projet numéro 6.

L'objectif demandé est de produire du code python permettant l'automatisation de tâche d'administration système.

Ici l'ensemble des scripts permet d'installer un serveur Wordpress sur une base LAMP dans un environnement Debian 10 et de configurer le https à l'aide d'un certificat auto-signé.

### installation-prerequis.py
Le premier script "installation-prerequis.py" comme son nom l'indique sert à installer les différents paquets nécessaires au bon fonctionnement du script ainsi que la base LAMP.

### configuration-https.py
Le deuxième script "configuration-https.py" sert à préparer https dans apache.
Il génère un groupe Diffie Hellmann si celui-ci n'existe pas et crée également un fichier de configuration apache pour SSL

### configuration-wordpress.py
Le troisième script "configuration-wordpress.py" sert à configurer la base MariaDB et produire les fichiers de conf apache et wordpress. Les différents identifiants et mots de passe sont saisis par l'utilisateur durant l'exécution du script.



