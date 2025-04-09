from .connexion import recupere_connexion_db
import mysql.connector
from mysql.connector import errorcode

# class pour le crud
class CRUD:
    
    # on creer un static method
    @staticmethod
    async def create( datas : dict ) :
        
        #on init la base de données
        login = recupere_connexion_db()
        # init cursor
        cnx  = login.cursor()
        try:
            #on creer la requete INSERT INTO
        
        
            print('connexion au serveur')
            return
        except mysql.connector.Error as err:
            print('Erreur : ', err)