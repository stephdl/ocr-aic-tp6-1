#!/usr/bin/python3
#-*- coding: utf8 -*-
"""

    configuration-https.py
    Script effectuant la configuration du https et la génération des certificats

    Auteur  :   Pierre LEMAIRE
    Version :   0.1
    Date    :   2021-05-17

    Testé avec Python 3.7 sous Debian 10 (Buster) stable
    forked by stephdl


"""

#Importation des modules nécessaires

import logging
import os
import subprocess

"""
    Tâches à effectuer : 
        - Configurer apache pour le ssl
        - Configurer le groupe Diffie Helman
"""

#Définition des constantes

LOG_FILE = "./configuration-https.log"

#Configuration du fichier de log

try:
    logging.basicConfig(filename=LOG_FILE, format="%(asctime)s : %(levelname)s:%(message)s",
            level=logging.DEBUG)
    logging.info("Début de la configuration https pour apache")
except Exception as e:
    print("")
    raise e

#Génération du groupe Diffie Hellmann afin d'améliorer la sécurité des certificats si le fichier n'existe pas
try:
    logging.info("Génération du fichier de groupe Diffie Hellmann /etc/ssl/certs/dhparam.pem")
    print("Génération du fichier de groupe Diffie Hellmann /etc/ssl/certs/dhparam.pem...")

    if not os.path.isfile("/etc/ssl/certs/dhparam.pem"):
        creation_dh_group = "openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048"
        os.system(creation_dh_group)
        logging.info("Le fichier a été créé avec succès")
        print("Le fichier a été créé avec succès !\n")

    else:
        logging.info("Le fichier existe déjà, il n'a pas été modifié")
        print("Le fichier existe déjà, il n'a pas été modifié.\n")

except Exception as e:
    logging.error("Echec de la création du fichier de groupe Diffie Hellmann")
    logging.error(e)
    raise e

#Génération du fichier /etc/apache2/conf-available/ssl-params.conf
try:
    ssl_params = [
            "SSLCipherSuite EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH\n",
            "SSLProtocol All -SSLv2 -SSLv3\n",
            "SSLHonorCipherOrder On\n",
            "Header always set Strict-Transport-Security \"max-age=63072000; includeSubdomains\"\n",
            "Header always set X-Frame-Options DENY\n",
            "Header always set X-Content-Type-Options nosniff\n",
            "SSLCompression off\n",
            "SSLSessionTickets Off\n",
            "SSLUseStapling on\n",
            "SSLStaplingCache \"shmcb:logs/stapling-cache(150000)\"\n",
            "SSLOpenSSLConfCmd DHParameters \"/etc/ssl/certs/dhparam.pem\"\n"
            ]

    logging.info("Création du fichier /etc/apache2/conf-available/ssl-params.conf")
    print("Création du fichier /etc/apache2/conf-available/ssl-params.conf...")
    
    if not os.path.isfile("/etc/apache2/conf-available/ssl-params.conf"):
        with open("/etc/apache2/conf-available/ssl-params.conf", "w") as ssl_params_file:
            ssl_params_file.writelines(ssl_params)
            logging.info("Le fichier a été créé avec succès")
            print("Le fichier a été créé avec succès !\n")
    else:
        logging.info("Le fichier ssl-params.conf existe déjà, il n'a pas été modifié")
        print("Le fichier ssl-params.conf existe déjà, il n'a pas été modifié.\n")
 
except Exception as e:
    logging.error("Echec de la création du fichier apache /etc/apache2/conf-available/ssl-params.conf")
    logging.error(e)
    raise e



