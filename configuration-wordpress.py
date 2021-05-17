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

#Configuration du fichier de log

try:
    logging.basicConfig(filename=LOG_FILE, format="%(asctime)s : %(levelname)s:%(message)s",
            level=logging.DEBUG)

except Exception as e:
    print("")
    raise e


