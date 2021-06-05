#!/usr/bin/python3
#-*- coding: utf8 -*-
"""

    configuration-wordpress.py
    Script effectuant la configuration du serveur LAMP et de Wordpress

    Auteur  :   Pierre LEMAIRE
    Version :   0.1
    Date    :   2021-05-17

    Testé avec Python 3.7 sous Debian 10 (Buster) stable


"""

#Importation des modules nécessaires

import logging
import os
import subprocess
import validators 
import apacheconfig
import mariadb
"""
    Tâches à effectuer : 
        - lire le nom et dns du serveur wordpress
        - créer et remplir le fichier /etc/apache2/sites-available/wp.conf
        - desactiver le site apache par défaut
        - activer le site apache wordpress
        - créer et remplir le fichier /etc/wordpress/config-MONDOMAINE.php
        - créer et remplir le fichier wp.sql qui va créer la base du site Wordpress dans MariaDB
        - créer la base SQL définie précedemment dans MariaDB 

"""

#Définition des constantes

LOG_FILE = "./configuration-wordpress.log"
APACHE_FILE = "/etc/apache2/sites-available/wp.conf"
DB_NAME = "wordpress"
DB_USER = "wordpress"
DB_PASSWORD = "password"
DB_HOST = "localhost"
WP_CONTENT_DIR = "/var/lib/wordpress/wp-content"
SERVER_NAME = "wordpress.local"
SERVER_ADMIN = "mail@mail"

#Configuration du fichier de log

try:
    logging.basicConfig(filename=LOG_FILE, format="%(asctime)s : %(levelname)s:%(message)s",
            level=logging.DEBUG)

except Exception as e:
    print("Echec de la création du fichier de log, l'installation n'a pas aboutie")
    raise e

#Lecture des variables

try:
    
    logging.info("Lecture des informations utilisateur")
    SERVER_NAME = input("Saisir le nom de domain complet (avec www. si besoin)\n")
    print(SERVER_NAME) 

    while not validators.domain(SERVER_NAME):
        SERVER_NAME = input("Veuillez saisir un nom de domain correct\n")
    
    logging.info("Nom de domaine saisi : {}".format(SERVER_NAME))
    
    DB_NAME = input("Saisir le nom de la base de données [{}]:\n".format(DB_NAME))                          or "wordpress"
    DB_USER = input("Saisir l'utilisateur de la base de données [{}]:\n".format(DB_USER))                   or "wordpress"
    DB_PASSWORD = input("Saisir le mot de passe de la base de données [{}]:\n".format(DB_PASSWORD))         or "password"
    DB_HOST = input("Saisir l'adresse de la base de données [{}]:\n".format(DB_HOST))                          or "localhost"
    WP_CONTENT_DIR = input("Saisir le répertoire de contenu wordpress [{}]:\n".format(
        WP_CONTENT_DIR)) or "/var/lib/wordpress/wp-content"
    SERVER_ADMIN = input("Saisir l'adresse mail de l'administrateur [{}]:\n".format(SERVER_ADMIN))          or "mail@mail"



except Exception as e:
    logging.error("Echec de la lecture des informations utilisateur")
    logging.error(e)
    raise e

#Création du fichier /etc/apache2/sites-available/wp.conf

try:

    apache_conf = [
        "<VirtualHost *:80>\n",
        "\tServerName {}\n".format(SERVER_NAME),
        "\tServerAdmin {}\n".format(SERVER_ADMIN),
        "\tDocumentRoot /usr/share/wordpress\n",
        "\tAlias /wp-content {}\n".format(WP_CONTENT_DIR), 
        "\tErrorLog ${APACHE_LOG_DIR}/error.log\n",
        "\tCustomLog ${APACHE_LOG_DIR}/access.log combined\n",
        "\t<Directory /usr/share/wordpress>\n",
        "\t\tOptions FollowSymLinks\n",
        "\t\tAllowOverride Limit Options FileInfo\n",
        "\t\tDirectoryIndex index.php\n",
        "\t\tRequire all granted\n",
        "\t</Directory>\n",
        "\t<Directory {}>\n".format(WP_CONTENT_DIR),
        "\t\tOptions FollowSymLinks\n"
        "\t\tRequire all granted\n"
        "\t</Directory>\n",
        "</VirtualHost>\n"
        ]

    with open("/etc/apache2/sites-available/wp.conf", "w") as apache_file:
        apache_file.writelines(apache_conf)
        logging.info("Le fichier /etc/apache2/sites-available/wp.conf a été créé avec succès")

except Exception as e:
    logging.error("Echec de la création du fichier wp.conf")
    logging.error(e)
    raise e

#Désactivation du site apache par défaut et activation du site Wordpress

try:
    os.system("a2dissite 000-default")
    os.system("a2ensite wp")
    os.system("systemctl reload apache2")
    logging.info("La configuration apache a été rechargée avec succès")

except Exception as e:
    logging.error("Echec du chargement de la nouvelle configuration Apache")
    logging.error(e)
    raise e

#Création du fichier PHP /etc/wordpress/config-SERVER_NAME.php

try:
    php_conf = [
            "<?php\n",
            "define('DB_NAME','{}');\n".format(DB_NAME),
            "define('DB_USER','{}');\n".format(DB_USER),
            "define('DB_PASSWORD','{}');\n".format(DB_PASSWORD),
            "define('DB_HOST','{}');\n".format(DB_HOST),
            "define('WP_CONTENT_DIR','{}');\n".format(WP_CONTENT_DIR),
            "?>\n"
            ]
    
    with open("/etc/wordpress/config-{}.php".format(SERVER_NAME), "w") as config_file_php:
        config_file_php.writelines(php_conf)
        logging.info("Le fichier /etc/wordpress/config-{}.php a été créé avec succès".format(SERVER_NAME))

except Exception as e:
    logging.error("Echec de la création du fichier de configuration php")
    logging.error(e)
    raise e 


#Création de la base dans MariaDB

#Définition d'une fonction qui crée/remplace une base de donnée dans mariadb
def creation_base(dico_base):
    try:
        with mariadb.connect(host = "localhost",
                user = "root",
                passwd = "OpenClassrooms21") as client_db:
            sql_create_cmd = "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER ON {}.* TO {}@{} IDENTIFIED BY '{}'".format(dico_base["DB_NAME"], dico_base["DB_USER"], dico_base["DB_HOST"], dico_base["DB_PASSWORD"])

            curseur_db = client_db.cursor()
            curseur_db.execute("DROP DATABASE IF EXISTS {}".format(dico_base["DB_NAME"]))
            curseur_db.execute("CREATE DATABASE {}".format(dico_base["DB_NAME"]))
            curseur_db.execute(sql_create_cmd)
            curseur_db.execute("FLUSH PRIVILEGES")
    
    except Exception as e:
        logging.error("Echec de la création de la base de données SQL dans MariaDB")
        raise e

try:
    sql_identifiants = {"DB_NAME": DB_NAME, "DB_USER": DB_USER, "DB_HOST": DB_HOST, "DB_PASSWORD": DB_PASSWORD}
        
    client_db = mariadb.connect(host = "localhost",
                                user = "root",
                                passwd = "OpenClassrooms21")

    curseur_db = client_db.cursor()
    curseur_db.execute("SHOW DATABASES")
    for x in curseur_db:

        if x[0] == DB_NAME:
            print("La base {} existe déjà, souhaitez-vous continuer quand même et écraser la base existante ? [O/Y]/n".format(
                x[0]))
            choix_erreur_db = input("") or "O"
            print(choix_erreur_db) 
            if choix_erreur_db == "O" or choix_erreur_db == "Y":
                client_db.close()
                print("OK on est des fous on supprime tout !")
                logging.info("La base '{}' existe déjà, elle va être réinitialisée".format(DB_NAME))
                creation_base(sql_identifiants)
                logging.info("La base '{}' a été réinitialisée".format(DB_NAME))
            else:
                print("Echec de création de la base, la base existe déjà.")
                logging.error("Echec de la création de la base SQL, la base existe déjà.")
                exit(os.EX_SOFTWARE)

        else:
            pass

except Exception as e:
    logging.error("Echec de la création de la base de donnée SQL dans MariaDB")
    logging.error(e)
    raise e   
