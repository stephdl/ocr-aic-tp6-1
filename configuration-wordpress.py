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
import mariadb

"""
    Tâches à effectuer : 
        - lire le nom et dns du serveur wordpress
        - créer et remplir le fichier /etc/apache2/sites-available/wp.conf
        - desactiver le site apache par défaut
        - activer le site apache wordpress
        - créer et remplir le fichier /etc/wordpress/config-MONDOMAINE.php
        - créer la base SQL dans MariaDB 
        - mettre en place 

"""

#Définition des constantes et variables

LOG_FILE = "./configuration-wordpress.log"
db_name = "wordpress"
dbuser = "wordpress"
db_password = "password"
db_host = "localhost"
WP_ROOT_DIR = "/usr/share/wordpress/"
WP_CONTENT_DIR = "/var/lib/wordpress/wp-content/"
server_name = "wordpress.local"
server_admin = "mail@mail"

MARIADB_ID = {"host": "localhost", "user": "root", "passwd": "OpenClassrooms21"}
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

    server_name = input("Saisir le nom de domain complet (avec www. si besoin)\n")
    #Je répète la saisie tant que le nom du serveur n'est pas un nom de domaine valide
    while not validators.domain(server_name):
        server_name = input("Veuillez saisir un nom de domain correct\n")

    logging.info("Nom de domaine saisi : {}".format(server_name))
    
    db_name = input("Saisir le nom de la base de données [{}]:\n".format(db_name))                          or "wordpress"
    dbuser = input("Saisir l'utilisateur de la base de données [{}]:\n".format(dbuser))                   or "wordpress"
    db_password = input("Saisir le mot de passe de la base de données [{}]:\n".format(db_password))         or "password"
    db_host = input("Saisir l'adresse de la base de données [{}]:\n".format(db_host))                          or "localhost"
    server_admin = input("Saisir l'adresse mail de l'administrateur [{}]:\n".format(server_admin))          or "mail@mail"

except Exception as e:
    logging.error("Echec de la lecture des informations utilisateur")
    logging.error(e)
    raise e

#Création du fichier /etc/apache2/sites-available/'server_name'.conf

try:
    #Représentation du contenu du fichier sous forme de liste
    apache_conf = [
        "<VirtualHost *:80>\n",
        "\tServerName {}\n".format(server_name),
        "\tServerAdmin {}\n".format(server_admin),
        "\tDocumentRoot {}\n".format(WP_ROOT_DIR),
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

    with open("/etc/apache2/sites-available/{}.conf".format(server_name), "w") as apache_file:
        apache_file.writelines(apache_conf)
        logging.info("Le fichier /etc/apache2/sites-available/{}.conf a été créé avec succès".format(server_name))

except Exception as e:
    logging.error("Echec de la création du fichier {}.conf".format(server_name))
    logging.error(e)
    raise e

#Désactivation du site apache par défaut et activation du site Wordpress

try:
    os.system("a2dissite 000-default")
    os.system("a2ensite {}".format(server_name))
    os.system("systemctl reload apache2")
    logging.info("La configuration apache a été rechargée avec succès")

except Exception as e:
    logging.error("Echec du chargement de la nouvelle configuration Apache")
    logging.error(e)
    raise e

#Création du fichier PHP /etc/wordpress/config-server_name.php

try:
    #Représentation du contenu du fichier sous forme de liste
    php_conf = [
            "<?php\n",
            "define('DB_NAME','{}');\n".format(db_name),
            "define('DB_USER','{}');\n".format(dbuser),
            "define('DB_PASSWORD','{}');\n".format(db_password),
            "define('DB_HOST','{}');\n".format(db_host),
            "define('WP_CONTENT_DIR','{}');\n".format(WP_CONTENT_DIR),
            "define('FS_METHOD','direct');\n",
            "?>\n"
            ]
    
    with open("/etc/wordpress/config-{}.php".format(server_name), "w") as config_file_php:
        config_file_php.writelines(php_conf)
        logging.info("Le fichier /etc/wordpress/config-{}.php a été créé avec succès".format(server_name))

except Exception as e:
    logging.error("Echec de la création du fichier de configuration php")
    logging.error(e)
    raise e 


#Création de la base dans MariaDB

#Définition d'une fonction qui indique l'existance d'une base de donnée dans mariadb
def existe_base(nom_base, identifiants):
    try:
        with mariadb.connect(host = identifiants["host"],
                user =identifiants["user"],
                passwd = identifiants["passwd"]) as client_db:
            
            curseur_db = client_db.cursor()
            curseur_db.execute("SHOW DATABASES")
            for x in curseur_db:
                if x[0] == nom_base:
                    return True
            
            return False

    except Exception as e:
        raise e

#Définition d'une fonction qui crée/remplace une base de donnée dans mariadb
def creation_base(dico_base):
    try:
        with mariadb.connect(host = "localhost",
                user = "root",
                passwd = "OpenClassrooms21") as client_db:
            sql_create_cmd = "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER ON {}.* TO {}@{} IDENTIFIED BY '{}'".format(dico_base["db_name"], dico_base["dbuser"], dico_base["db_host"], dico_base["db_password"])

            curseur_db = client_db.cursor()
            curseur_db.execute("DROP DATABASE IF EXISTS {}".format(dico_base["db_name"]))
            curseur_db.execute("CREATE DATABASE {}".format(dico_base["db_name"]))
            curseur_db.execute(sql_create_cmd)
            curseur_db.execute("FLUSH PRIVILEGES")
    
    except Exception as e:
        logging.error("Echec de la création de la base de données SQL dans MariaDB")
        raise e

#Création de la base de données SQL
try:
    sql_identifiants = {"db_name": db_name, "dbuser": dbuser, "db_host": db_host, "db_password": db_password}

    client_db = mariadb.connect(host = "localhost",
                                user = "root",
                                passwd = "OpenClassrooms21")

    curseur_db = client_db.cursor()
    curseur_db.execute("SHOW DATABASES")

    if existe_base(db_name, MARIADB_ID):
        print("La base {} existe déjà, souhaitez-vous continuer quand même et écraser la base existante ? [O/Y]/n".format(
            db_name))
        choix_erreur_db = input("") or "O"
        print(choix_erreur_db) 
        if choix_erreur_db == "O" or choix_erreur_db == "Y":
            client_db.close()
            print("OK on est des fous on supprime tout !")
            logging.info("La base '{}' existe déjà, elle va être réinitialisée".format(db_name))
            creation_base(sql_identifiants)
            logging.info("La base '{}' a été réinitialisée".format(db_name))
        else:
            print("Echec de création de la base, la base existe déjà.")
            logging.error("Echec de la création de la base SQL, la base existe déjà.")
            exit(os.EX_SOFTWARE)

    else:
        creation_base(sql_identifiants)

except Exception as e:
    logging.error("Echec de la création de la base de donnée SQL dans MariaDB")
    logging.error(e)
    raise e   

#Création des certificats ssl
try:
    creation_cert = "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/{}-selfsigned.key -out /etc/ssl/certs/{}-selfsigned.crt".format(server_name, server_name)
    
    creation_dh_group = "openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048"
    
    print("Création des certificats auto-signés")
    
    os.system(creation_cert)
#    os.system(creation_dh_group)
    logging.info("Certificats auto-signés créés avec succès")

except Exception as e:
    logging.error("Echec de la création des certificats")
    logging.error(e)
    raise e
#Configuration d'Apache pour HTTPS
try:
    #Représentation du contenu du fichier sous forme de liste
    apache_https_conf = [
            "<IfModule mod_ssl.c>\n",
            "<VirtualHost *:443>\n",
            "\tServerName {}\n".format(server_name),
            "\tServerAdmin {}\n".format(server_admin),
            "\tDocumentRoot {}\n".format(WP_ROOT_DIR),
            "\tAlias /wp-content {}\n".format(WP_CONTENT_DIR), 
            "\tErrorLog ${APACHE_LOG_DIR}/error.log\n",
            "\tCustomLog ${APACHE_LOG_DIR}/access.log combined\n",
            "\tSSLEngine on\n",
            "\tSSLCertificateFile   /etc/ssl/certs/{}-selfsigned.crt\n".format(server_name),
            "\tSSLCertificateKeyFile    /etc/ssl/private/{}-selfsigned.key\n".format(server_name),
            "\t<FilesMatch \"\.(cgi|shtml|phtml|php)$\">\n",
            "\t\tSSLOptions +StdEnvVars\n",
            "\t</FilesMatch>\n",
            "\t<Directory /usr/share/wordpress>\n",
            "\t\tOptions FollowSymLinks\n",
            "\t\tAllowOverride Limit Options FileInfo\n",
            "\t\tDirectoryIndex index.php\n",
            "\t\tRequire all granted\n",
            "\t</Directory>\n",
            "\t<Directory {}>\n".format(WP_CONTENT_DIR),
            "\t\tOptions FollowSymLinks\n",
            "\t\tRequire all granted\n",
            "\t</Directory>\n",
            "</VirtualHost>\n",
            "</Ifmodule>\n",
            "<VirtualHost *:80>\n",
            "\tServerName {}\n".format(server_name),
            "\tRedirect permanent / https://{}\n".format(server_name),
            "</VirtualHost>\n"
        ]

    with open("/etc/apache2/sites-available/{}.conf".format(server_name), "w") as apache_https_file:
        apache_https_file.writelines(apache_https_conf)
        logging.info("Le fichier /etc/apache2/sites-available/{}.conf a été modifié avec succès".format(server_name))
    os.system("a2enmod ssl")
    os.system("a2enmod headers")
    os.system("a2enconf ssl-params")
    os.system("apache2ctl configtest")
    os.system("systemctl restart apache2.service")




except Exception as e:
    logging.error("Echec de la configuration HTTPS d'Apache")
    logging.error(e)
    raise e
