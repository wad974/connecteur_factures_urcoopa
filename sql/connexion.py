import mysql.connector
import os
from dotenv import load_dotenv

#on init les variables d'environnement pour connexion base de données
load_dotenv()

def recupere_connexion_db() :
    #connexion au serveur
    login  = mysql.connector.connect(
        host= os.getenv('DB_URL_HOST'), 
        port= os.getenv('DB_URL_PORT'),
        user= os.getenv('DB_URL_USER'),
        password= os.getenv('DB_URL_PASSWORD'),
        database= os.getenv('DB_URL_DATABASE')
    )
    
    return login


