from .connexion import recupere_connexion_db
import mysql.connector
from mysql.connector import errorcode

# class pour le crud
class CRUD:
    
    def __init__(self):
        
        #on init la base de données
        self.connexion = recupere_connexion_db()
    
    # on creer un static method CREATE
    @staticmethod
    async def create(self, datas : dict ) :
        
        # init cursor
        cnx  = self.connexion
        try:
            #on creer la requete INSERT INTO
        
        
            print('connexion au serveur')
            return
        except mysql.connector.Error as err:
            print('Erreur : ', err)
    
            
    # on creer un static method READ
    @staticmethod
    async def read(self, datas : dict ) :
        
        # init cursor
        cnx  = self.connexion

        try:
            #on creer la requete SELECT
        
        
            print('connexion au serveur')
            return
        except mysql.connector.Error as err:
            print('Erreur : ', err)

    
    # on creer un static method UPDATE
    @staticmethod
    async def update(self, datas : dict ) :
        
        # init cursor
        cnx  = self.connexion

        try:
            #on creer la requete UPTADE 
        
        
            print('connexion au serveur')
            return
        except mysql.connector.Error as err:
            print('Erreur : ', err)
            
    
    # on creer un static method DELETE
    @staticmethod
    async def delete(self, datas : dict ) :

        # init cursor
        cnx  = self.connexion

        try:
            #on creer la requete DELETE (SI BESOIN)
        
        
            print('connexion au serveur')
            return
        except mysql.connector.Error as err:
            print('Erreur : ', err)