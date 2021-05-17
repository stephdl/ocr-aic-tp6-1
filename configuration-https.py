#!/usr/bin/python3
#-*- coding: utf8 -*-
"""

    configuration-https.py
    Script effectuant la configuration du https et la génération des certificats

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
        - Générer les certificats
        - Configurer apache pour le ssl
        - Vérifier la conf Apache
        - Configurer la redirection http -> https
"""

#Définition des constantes

LOG_FILE = "./configuration-https.log"

#Configuration du fichier de log

try:
    logging.basicConfig(filename=LOG_FILE, format="%(asctime)s : %(levelname)s:%(message)s",
            level=logging.DEBUG)

except Exception as e:
    print("")
    raise e


