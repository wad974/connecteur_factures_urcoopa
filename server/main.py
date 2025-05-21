from fastapi import FastAPI, Form, HTTPException
import zeep
import json
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import base64
import datetime
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from sql.models import CRUD
import mysql.connector
import numpy as np
import pandas as pd

from datetime import datetime

from ConnectOdooFramework import createOdoo
from createOdoo import createOdoo


# Chargement des variables d'environnement
load_dotenv()

#Récupération des variables d'environnement
WSDL_URL = os.getenv('MY_URCOOPA_URL')
API_KEY_URCOOPA = os.getenv('API_KEY_URCOOPA')

# Vérification des variables requises
if not all([WSDL_URL, API_KEY_URCOOPA]):
    raise ValueError("Toutes les variables d'environnement (WSDL_URL et API_KEY_URCOOPA) doivent être définies.")

client = zeep.Client(wsdl=WSDL_URL)  # on crée le client

app = FastAPI()

# Dossier templates
templates = Jinja2Templates(directory="templates")

# Monter les fichiers statiques à l'URL /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplacez par l'URL de votre front-end
    allow_credentials=True,
    allow_methods=["*"],  # Méthodes HTTP autorisées
    allow_headers=["*"],  # En-têtes autorisés
)


######## HOME / RACINE
@app.get('/', response_class=HTMLResponse)
def home(request : Request):
    return templates.TemplateResponse(
        'index.html', 
        {
            "request" : request, 
            'title' : 'Accueil',
            'year' : datetime.now().year
        })

### FACTURES

@app.get("/factures/")
async def get_factures(xCleAPI: str = API_KEY_URCOOPA, nb_jours: int = 30):
    try:
        print("🟢 INIT : Démarrage du service get_factures...")
        
        response = client.service.Get_Factures_Sicalait(xCleAPI=xCleAPI, NbJours=nb_jours)
        
        if not response:
            raise HTTPException(status_code=404, detail="Aucune facture trouvée.")
        
        factures = json.loads(response)
        
        # boucles sur factures pour recuperer les datas json
        crud = CRUD()
        
        Adherent = []
        Urcoopa = []
        
        for row in factures:
            
            # Récuperation numéros facture
            # Vérification que numéros facture existe dans Bases de données
            # resultat = [] ou dict 
            numero_facture = row.get("Numero_Facture")
            resultat = await crud.read(numero_facture)
            
            #print(f'retour resultat read : {resultat}')
            
            if len(resultat) == 0:
                print(f"Facture {numero_facture} absente BDD ➔ Création")
                await crud.create(row)
                
                
                '''     
                # Comparer l'existant avec le nouveau row
                if not crud.est_meme_facture(resultat, row):
                    print(f"Facture {numero_facture} différente ➔ Update")
                    #await crud.update(row)
                else:
                '''         
            
            
            print(f"Facture {numero_facture} déjà creer BDD ➔ Injection ODOO")
            Urcoopa.append(row)
            print('✅ AJOUT DANS TABLEAU URCOOPA \n\n')
            
            
        if Urcoopa:
            from collections import defaultdict

            factures_groupées = defaultdict(list)

            for row in Urcoopa:
                factures_groupées[row["Numero_Facture"]].append(row)

            for numero_facture, lignes in factures_groupées.items():
                # On filtre : ne traiter que les lignes NON ADHERENT
                lignes_filtrées = [row for row in lignes if row.get("Type_Client") != "ADHERENT"]

                if lignes_filtrées:
                    # Appel unique à createOdoo avec toutes les lignes de cette facture
                    await createOdoo(lignes_filtrées)
        
        '''  
        #Filtres Adherent  / Magasin
        if row.get('Type_Client') != 'ADHERENT':
            #create dans facture odoo
            result = await createOdoo(row)
            
            
        else: 
            #create facture dans petit module odoo comptaAdherent
            Adherent.append(row)
        ''' 
        
        
        return JSONResponse(content=Urcoopa, status_code=200 )       
        #return {"Messages": 'Récuperation factures urcoopa Ok !'}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de décodage JSON.")
    except zeep.exceptions.Fault as fault:
        raise HTTPException(status_code=500, detail=f"Erreur SOAP : {fault}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

######################################################
#recuperation adherent dans base de données exportOdoo
@app.get('/factureAdherentUrcoopa', response_class=HTMLResponse)
async def getFactureAdherentUrcoopa( request : Request ):
    try: 
        print(' 🌐 init')
        #connexion base de données
        connexion = mysql.connector.connect(
            host = '172.17.240.18',#host,
            port='3306',
            database= 'exportodoo', #dbname 
            user='root', #user
            password='S1c@l@1t'
        )
        print('🌐 connexion', connexion)
        # on recupere le cursor en dictionnaire
        cursorRequete = connexion.cursor(dictionary=True)
        
        # on execute la requete sur la table sic urcoopa facture where champs adherent
        requete = '''
                SELECT * FROM sic_urcoopa_facture
                WHERE Type_Client = 'ADHERENT'
                ORDER BY Nom_Client ASC
        '''
        cursorRequete.execute(requete,)
        
        # on recupere la requete
        datas = cursorRequete.fetchall()
        print('✅ récupération datas ok !')
        
        query  = '''
                SELECT
                f.Numero_Facture,
                f.Type_Facture,
                f.Date_Facture,
                f.Date_Echeance,
                f.Societe_Facture,
                f.Code_Client,
                f.Nom_Client,
                f.Type_Client,
                f.Montant_HT,
                f.Montant_TTC,
                f.Numero_Ligne_Facture,
                f.Code_Produit,
                f.Libelle_Produit,
                f.Prix_Unitaire,
                f.Quantite_Facturee,
                f.Unite_Facturee,
                f.Numero_Silo,
                f.Montant_HT_Ligne,
                f.Taux_TVA,
                f.Depot_BL,
                f.Numero_BL,
                f.Numero_Ligne_BL,
                f.Commentaires,
                f.Numero_Commande_Client,
                f.Date_Commande_Client,
                f.Numero_Commande_ODOO,
                f.Code_Produit_ODOO,
                f.ID_Produit_ODOO,
                f.Code_Client_ODOO,
                f.ID_Client_ODOO,
                f.Societe_Facture_ODOO,
                f.ID_Facture_ODOO,
                p.id
                FROM exportodoo.sic_urcoopa_facture f
                left join exportodoo.res_partner p
                on f.Nom_Client = p.name
                where Type_Client ='ADHERENT'
                ORDER BY Nom_Client ASC
        '''
        cursorRequete.execute(query,)
        
        # on recupere la requete
        adherent_null = cursorRequete.fetchall()
        print('✅ récupération adherent_null ok !')
        
        #on ferme la connexion
        cursorRequete.close()
        connexion.close()
        
        # ✅ Calcul des totaux côté serveur
        total_ht = sum(f["Montant_HT"] for f in datas)
        total_ttc = sum(f["Montant_TTC"] for f in datas)
        
        #filtre somme client
        df = pd.DataFrame(datas)
        regroupe = df.groupby(['Code_Client', 'Nom_Client' ])[['Montant_HT', 'Montant_TTC']].sum().reset_index()
        regroupé_dicts = regroupe.to_dict(orient='records')
        
        print(regroupé_dicts)
        
        
        
        # affiche uniquement les adherent_nul
        facture_adherent_null = []
        for row in adherent_null:
            
            if row.get('id') == None:
                facture_adherent_null.append(row)
        
        df = pd.DataFrame(facture_adherent_null)
        regroupe_non_adherent = df.groupby(['Code_Client', 'Nom_Client' ])[['Montant_HT', 'Montant_TTC']].sum().reset_index()
        regroupe_non_adherent = regroupe_non_adherent.to_dict(orient='records')
        
        print(regroupe_non_adherent)
        
        return JSONResponse(content=regroupé_dicts)
        
        '''
        return templates.TemplateResponse( 
                                        'factures.html', 
                                        { 
                                            'request' : request,
                                            'factures' : regroupé_dicts ,
                                            "total_ht": total_ht,
                                            "total_ttc": total_ttc,
                                            'adherent_null' : regroupe_non_adherent,
                                            "year": datetime.now().year
                                        })
        '''
        
    except mysql.connector.Error as erreur:
        print(f'Erreur lors de la connexion à la base de données : {erreur}')
        return {"Erreur connexion Base de données : {erreur}"}
    
    
# POST BOUTONVALID

@app.post("/valider-facture", response_class=HTMLResponse)
async def valider_facture(
    request: Request,
    numero_facture: str = Form(...),
    code_client: str = Form(...),
    montant_ht: float = Form(...)
):
    
    #connexion sql
    print(' 🌐 init')
    #connexion base de données
    connexion = mysql.connector.connect(
            host = '172.17.240.18',#host,
            port='3306',
            database= 'exportodoo', #dbname 
            user='root', #user
            password='S1c@l@1t'
        )
    print('🌐 connexion', connexion)
    # on recupere le cursor en dictionnaire
    cursorRequete = connexion.cursor(dictionary=True)
    
    requete = '''
                update sic_urcoopa_facture
                set Numero_Facture = '%s'
                where Numero_Facture = '%s'
        '''
    new_numero_facture = 'val'+numero_facture
    datas = (new_numero_facture, numero_facture)
    cursorRequete.execute(requete,datas,)
    connexion.commit()
    # utiliser les données ici
    print(f"Facture {numero_facture} validée pour le client {code_client} - ht : {montant_ht}€ - ttc : ")

    # rediriger, stocker, ou afficher une page de confirmation
    return templates.TemplateResponse("confirmation.html", {
        "request": request,
        "numero_facture": numero_facture,
        "code_client": code_client,
        "montant_ht": montant_ht
    })

from crontab import CronTab
def init_cron():
    # Récupération de la planification via variable d'environnement
    #cron_schedule = os.getenv('CRONTAB_APP', '30 14 * * *')
    cron_schedule = os.getenv('CRONTAB_APP')

    # Initialisation du cron pour l'utilisateur root
    #cron = CronTab(user='root')
    cron = CronTab(user='root')
    cron.remove_all()
    cron.write()

    # Définition de la commande
    job = cron.new(command='curl http://0.0.0.0:9898/factures/?xCleAPI=f1f3b6d5-113e-4cd1-943d-0f07d28000df&nb_jours=30')
    job.setall(cron_schedule)
    cron.write()

    # Lancement du service cron
    print(f"✅ CRON configuré avec la planification : {cron_schedule}")
    print("✅ Démarrage du service CRON...")
    os.system('service cron start')
    print("✅ Service CRON lancé avec succès.")

init_cron()

if __name__ == "__main__":
    
    
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=9898,
        #ssl_certfile="server.crt",
        #ssl_keyfile="server.key"
        )
