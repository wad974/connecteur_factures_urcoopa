from fastapi import FastAPI, Form, HTTPException
import zeep
from zeep import xsd
import json
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import base64
from datetime import datetime , timedelta
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import zeep.exceptions
from zeep.exceptions import Fault
from sql.models import CRUD
import mysql.connector
import numpy as np
import pandas as pd

from datetime import datetime

from ConnectOdooFramework import createOdoo
from createOdoo import createOdoo
from createOdooGesica import createOdooGesica


# Chargement des variables d'environnement
load_dotenv()

#Récupération des variables d'environnement
WSDL_URL = os.getenv('MY_URCOOPA_URL')
API_KEY_URCOOPA = os.getenv('API_KEY_URCOOPA')
API_KEY_JOUR = os.getenv('API_KEY_JOUR')

# Vérification des variables requises
if not all([WSDL_URL, API_KEY_URCOOPA]):
    raise ValueError("Toutes les variables d'environnement (WSDL_URL et API_KEY_URCOOPA) doivent être définies.")

client = zeep.Client(wsdl=WSDL_URL)  # on crée le client

app = FastAPI()

# Monter les fichiers statiques à l'URL /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dossier templates
templates = Jinja2Templates(directory="templates")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplacez par l'URL de votre front-end
    allow_credentials=True,
    allow_methods=["*"],  # Méthodes HTTP autorisées
    allow_headers=["*"],  # En-têtes autorisés
)

# ---------------------
# 0. 📦 Connexion à la commande Odoo
# ---------------------

print('📤[INFO] Début connexion odoo')
from collections import defaultdict
import xmlrpc.client
            
# Paramètres
url = 'https://sdpmajdb-odoo17-dev-staging-sicalait-20406522.dev.odoo.com/'
db = 'sdpmajdb-odoo17-dev-staging-sicalait-20406522'
username = 'info.sdpma@sicalait.fr'
password = 'nathalia974'

# Authentification
info = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = info.authenticate(db, username, password, {})

if not uid:
    print("❌ Échec de l'authentification.")

print(f"✅ Authentification réussie. UID: {uid} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} \n\n")
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

#connexion base de données
print('🌐 init')
connexion = mysql.connector.connect(
    host = '172.17.240.18',#host,
    port='3306',
    database= 'exportodoo', #dbname 
    user='root', #user
    password='S1c@l@1t'
)
print('🌐 connexion', connexion)

######## HOME / RACINE
@app.get('/', response_class=HTMLResponse)
def home(request : Request):
    try: 
        print('🌐 init')
        
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
        
        #print(regroupé_dicts)
        
        # affiche uniquement les adherent_nul
        facture_adherent_null = []
        for row in adherent_null:
            
            if row.get('id') == None:
                facture_adherent_null.append(row)
        
        df = pd.DataFrame(facture_adherent_null)
        regroupe_non_adherent = df.groupby([ 'Numero_Facture', 'Code_Client', 'Nom_Client', 'Date_Facture', 'Date_Echeance' ])[['Montant_HT', 'Montant_TTC']].sum().reset_index()
        regroupe_non_adherent = regroupe_non_adherent.to_dict(orient='records')
        
        #print(regroupe_non_adherent)
        #return JSONResponse(content=regroupé_dicts)
        
        
        return templates.TemplateResponse( 
                                        'index.html', 
                                        { 
                                            'request' : request,
                                            'factures' : regroupé_dicts ,
                                            "total_ht": total_ht,
                                            "total_ttc": total_ttc,
                                            'adherent_null' : regroupe_non_adherent,
                                            "year": datetime.now().year
                                        })
        
        
    except mysql.connector.Error as erreur:
        print(f'Erreur lors de la connexion à la base de données : {erreur}')
        return {"Erreur connexion Base de données : {erreur}"}
    '''
    return templates.TemplateResponse(
        'index.html', 
        {
            "request" : request, 
            'title' : 'Accueil',
            'year' : datetime.now().year
        })
    '''


#GET COMMANDES DEPUIS GESICA
@app.get('/Commandes_Gesica')
async def get_commandes_gesica():
    
    try:
        crud = CRUD()
        resultat = await crud.readAll()
        purchase = defaultdict(list)

        for index, row in enumerate(resultat):
            #print(f'\n Boucle => {index + 1} \n')
            purchase[row["ENOCOM"]].append(row)

        max_factures = 2
        for i, (numero_facture, lignes) in enumerate(purchase.items()):
            print(f'📦 Traitement de la facture {numero_facture} contenant {len(lignes)} lignes')

            if i >= max_factures:
                print(f"🔔 Limite atteinte ({max_factures} factures). Arrêt du traitement.")
                break
            
            # Appel à createOdooGesica pour construire la commande
            commande_odoo = await createOdooGesica(
                lignes, models, db, uid, password
            )

            print('commande odoo', commande_odoo)
            if commande_odoo:
                
                try:
                    move_id = models.execute_kw(
                        db, uid, password,
                        'purchase.order', 'create',
                        [commande_odoo]
                    )
                    print(f"✅📤 Commande Odoo créée avec ID {move_id} pour facture {numero_facture}")
                except xmlrpc.client.Fault as e:
                    print(f"❌ Erreur XML-RPC Odoo : {e.faultString}")
                    
        #print('RETOUR PURCHASE ', purchase)
        return JSONResponse(content={"message": "Import terminé avec succès."}, status_code=200)

    except Exception as e:
        print(f'ERREUR: {e}')
        raise HTTPException(status_code=500, detail=str(e))


### FACTURES
@app.get("/factures/")
async def get_factures(xCleAPI: str = API_KEY_URCOOPA, nb_jours: int = API_KEY_JOUR):
    try:
        print("🌐 INIT : Démarrage du service get_factures...")
        
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
            print('✅ [SUCCESS] Fin ajout facture bdd')
            print('📤[INFO] Début ajout facture Odoo')
            
            
            factures_groupées = defaultdict(list)

            for row in Urcoopa:
                factures_groupées[row["Numero_Facture"]].append(row)

            for numero_facture, lignes in factures_groupées.items():
                # On filtre : ne traiter que les lignes NON ADHERENT
                lignes_filtrées = [row for row in lignes if row.get("Type_Client") != "ADHERENT"]

                if lignes_filtrées:
                    # Appel unique à createOdoo avec toutes les lignes de cette facture
                    await createOdoo(lignes_filtrées,models, db, uid, password )
                    
        
        '''  
        #Filtres Adherent  / Magasin
        if row.get('Type_Client') != 'ADHERENT':
            #create dans facture odoo
            result = await createOdoo(row)
            
            
        else: 
            #create facture dans petit module odoo comptaAdherent
            Adherent.append(row)
        ''' 
        
        print('✅📤 [SUCCESS] IMPORT FACTURE URCOOPA EFFECTUE !')
        return JSONResponse(content=Urcoopa, status_code=200 )       
        #return {"Messages": 'Récuperation factures urcoopa Ok !'}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de décodage JSON.")
    except zeep.exceptions.Fault as fault:
        raise HTTPException(status_code=500, detail=f"Erreur SOAP : {fault}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
#PUSH FACTURES
@app.post("/envoyer-commande/")
#@app.post("/envoyer-commande/{commande_id}")
#async def envoyer_commande(commande_id: int):
async def envoyer_commande():

    try:
        print('[INFO] 🌐 init commande')
        
        #filtre par date
        
        date_end = datetime.now() # on recupere la date maintenant (int)
        date_start = date_end - timedelta(days=5) # on soustrait 2jours (int)
        #date_start = date_end - timedelta(days=int(os.getenv('DATE_JOUR'))) # on soustrait 2jours (int)

        date_start_new = date_start.strftime('%Y-%m-%d 00:00:00') # date de départ strftime
        date_end_new = date_end.strftime('%Y-%m-%d 23:59:59') # date fin str
    
        commandes = models.execute_kw(
            db, uid, password,
            'purchase.order',
            #'search',
            'search_read',
            #'search_count',
            [[
                ['date_order', '>=', date_start_new], #depart Jours - 2
                ['date_order', '<=', date_end_new] # fin jours present
            ]],
            {
                #'limit' : 10,
                'order': 'id desc'
            }
        )
        
        #filtres 
        for commande in commandes:
            #print(commande.get('partner_id'), commande.get('state'))
            partner_urcoopa = commande.get('partner_id')
            
            #filtre par urcoopa
            if partner_urcoopa[1] != 'URCOOPA':
                print('[FAULT] ❌ FAUSSE ALERTE - NON URCOOPA ', partner_urcoopa , '\n')
                continue
                
            print('[SUCCESS] ✅  BINGO URCOOPA')      
            # ---------------------
            # 1. 📦 Récupérer la commande Odoo
            # ---------------------
            print('[INFO] 1. 📦 Récupération de la commande Odoo')
            commande_id = models.execute_kw(
                db, uid, password,
                'purchase.order', 'read',
                [[commande.get('id')]],  # filtre, sur le id de la commande
                {
                    'fields' : ['name', 'partner_id', 'company_id', 'date_order', 'order_line', 'state']
                    #'limit': 1,
                    #'order': 'id desc'  # trie du plus grand ID au plus petit
                }
            )[0]
            #print("[INFO] 🆔 Dernier ID créé dans purchase.order :", commande_id)
            
            #FILTRES : commandes urcoopa uniquement
            #FILTRES : status : draft 
            if commande['partner_id'][1] == 'URCOOPA' and commande.get('state') == 'purchase':
                
                print('[INFO] 2. 📦 Récupérer le partner Odoo')
                partner = models.execute_kw(
                    db, uid, password,
                    'res.partner', 'read',
                    [[commande['partner_id'][0]]],
                    {'fields': ['name']}
                )[0]
                print('[SUCCESS] ✅ Partner Odoo récupéré : ', partner)
                
                #recuperation info : login mail societe
                print('COMMANDE : ', commande['user_id'])
                info_user = models.execute_kw(
                    db, uid, password,
                    #'purchase.order.line', 'search_read',
                    'res.users', 'search_read',
                    [[[ 'id', '=', commande['user_id'][0] ]]],  # pas de filtre, on veut tout
                    {
                        #'limit': 10,
                        #'order': 'id asc' , # trie du plus grand ID au plus petit
                        'fields' : ['name', 'email', 'phone', 'company_id']
                    }
                )[0]
                print('[SUCCESS] ✅ info_user Odoo récupéré : ', info_user)
                
                shipping = models.execute_kw(db, uid, password,
                    'res.partner', 'read', [[commande['partner_id'][0]]],
                    {'fields': ['name']}
                )[0]
                
                print('[SUCCESS] ✅ shipping Odoo récupéré', shipping )

                # Récupérer les lignes de la commande
                products = models.execute_kw(
                    db, uid, password,
                    'purchase.order.line', 'read',
                    [commande['order_line']],
                    {'fields': ['product_id', 'name', 'product_qty']}
                )
                print('[INFO] 📦 Produits récupéré')
                #print('[INFO] 📦 Voici les produits  : ', json.dumps(products, indent=2))

                commentaire = ''
                # ---------------------
                # 2. 🏗️ Construire le JSON à envoyer
                # ---------------------
                ligne_commande = []
                for i, ligne in enumerate(products):
                    
                    #conditions pour recupéré products s'il y a commentaire
                    if not ligne['product_id']:
                        commentaire += f" - {ligne['name']} ;"
                        print('-> commentaire : ', commentaire)
                        continue
                    
                    product_id = ligne['product_id'][0]
                    #print('-> product_id récupéré: ', product_id)
                    
                    # Récupérer le product_tmpl_id
                    product_product = models.execute_kw(
                        db, uid, password,
                        'product.product', 'read',
                        [[product_id]],
                        {'fields': ['product_tmpl_id']}
                    )[0]
                    product_tmpl_id = product_product['product_tmpl_id'][0]
                    #print('-> product_tmpl_id récupéré: ', product_tmpl_id)
                    
                    # Chercher les ids supplierinfo
                    supplierinfo_ids = models.execute_kw(
                        db, uid, password,
                        'product.supplierinfo', 'search',
                        [[['product_tmpl_id', '=', product_tmpl_id]]]
                    )
                    #print('-> supplierinfo_ids récupéré: ', supplierinfo_ids)
                    
                    
                    # Lire les infos product code à enlever si besoin
                    product_code = 'N/A'
                    if supplierinfo_ids:
                        
                        supplierinfo_data = models.execute_kw(
                            db, uid, password,
                            'product.supplierinfo', 'read',
                            [supplierinfo_ids],
                            {'fields': ['product_code']}
                        )
                        #if supplierinfo_data and supplierinfo_data[0].get('product_code'):
                        for row in supplierinfo_data:
                            if row['product_code']:
                                product_code = row['product_code']
                                print('[INFO] Code supplierinfo_product_code récupéré :', product_code)

                    print('[INFO] Code fournisseur récupéré :', product_code)
                    
                    
                    
                    # Extrait code interne si besoin ( code dans crochets)
                    code_interne = ligne['name'].split("]")[0].replace("[", "")
                    
                    ligne_commande.append({
                        "Numero_ligne": i + 1,
                        "Code_Produit": product_code,
                        "Libelle_Produit": ligne['name'],
                        "Poids_Commande": ligne['product_qty']
                    })
                
                
                #print('[INFO] 📦 lignes produits Commandes final : ', json.dumps(ligne_commande, indent=2))
                print('[INFO] 📦 lignes produits Commandes final OK!')
                
                #on enleve gesica
                reference_partenaire = commande.get('partner_ref')
                
                if reference_partenaire:
                    reference = reference_partenaire.replace('GESICA', "").strip()
                else :
                    reference = commande.get('name').strip()
                    
                #requete code client
                if not commande['company_id']:
                    continue
                else:
                    print( '\n📤 [INFO] REQUETE SQL CODE COMPANY_ID ODOO : ', json.dumps( commande['company_id'][0], indent=2 ))
                    code = commande['company_id'][0] 
                    #print(json.dumps( commande, indent=2 ))          
                    
                    #requete sic_depot
                    print('🌐 init SQL')
                    
                    # on recupere le cursor en dictionnaire
                    cursorRequete = connexion.cursor(dictionary=True)
                    
                    # on execute la requete sur la table sic urcoopa facture where champs adherent
                    requete = '''
                            SELECT * FROM sic_depot
                            WHERE company_id = %s
                    '''
                    
                    code_urcoopa = ( code,)
                    cursorRequete.execute(requete, code_urcoopa)
                    
                    # on recupere la requete
                    datas = cursorRequete.fetchall()
                    print('✅ récupération datas ok !', datas)
                    #print(json.dumps(datas, indent=2))
                    
                    if len(datas) == 0 or datas[0].get('code_urcoopa') is None:
                        code_client = "0000"
                        print('Code_Client :', code_client)
                    
                    else: 
                        #"Code_Client": "5024",
                        code_client = datas[0].get('code_urcoopa')
                    
                commande_json = {
                    "Commande": [
                        {
                            "Societe": "UR",
                            #"Code_Client": "5024",
                            "Code_Client": code_client,
                            "Numero_Commande": reference,
                            "Nom_Client": json.loads(f'"{commande.get('picking_type_id')[1]}"'),
                            "Code_Adresse_Livraison": "01",
                            "Commentaire": commentaire,
                            "Date_Livraison_Souhaitee": commande["date_order"].replace("-", "")[:8],
                            "Num_Telephone": info_user.get("phone", ""),
                            "Email": info_user.get("email", ""),
                            "Ligne_Commande": ligne_commande
                        }
                    ]
                }
                
                print("\n✅ Commande construite finale :", json.dumps(commande_json, indent=2, ensure_ascii=False), '\n\n')
                
                # ---------------------
                # 3. 📤 Envoi via SOAP
                # ---------------------
                
                commande_json_str = json.dumps(commande_json)
                jCommande_type = xsd.Element(
                    '{urn:WS_Sicalait}jCommande',
                    xsd.String()
                )
                jCommande_value = jCommande_type(commande_json_str)
                
                response = client.service.Push_Commandes_Sicalait(
                    xCleAPI=API_KEY_URCOOPA,
                    jCommande=jCommande_value
                )
                
                print("[INFO] ", response)
                
                #on décortique pour vérifier qu'il y a erreur ou pas
                response = response.split()
                
                if response[0] == 'ERREUR':
                    print("[ERREUR] ❌ Réponse Urcoopa \n\n")
                    continue
                    #return JSONResponse(content={"status": "DONE", "response": response})
                else :
                    print('✅[INFO] COMMANDE ENVOYER')
                    continue
                    ###
                    ###FILTRES A METTRE EN PLACE POUR COMMANDE DEJA ENVOYER SI NECESSAIRE
                    ###
                    ###
                    #return JSONResponse(content={"status": "OK", "response": response})
                    
            else : 
                print('[FAULT] ❌ ZUT COMMANDE TOUJOURS EN BROUILLON \n')    
                
    except Fault as soap_err:
        print("❌ Erreur SOAP :", soap_err)
        raise HTTPException(status_code=500, detail=str(soap_err))
    '''
    except Exception as e:
        print("❌ Erreur générale :", e)
        raise HTTPException(status_code=500, detail=str(e))
    '''
######################################################
#recuperation adherent dans base de données exportOdoo
@app.get('/factureAdherentUrcoopa', response_class=HTMLResponse)
async def getFactureAdherentUrcoopa( request : Request ):
    try: 
        print('🌐 init')
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
        
        #print(regroupé_dicts)
        
        
        
        # affiche uniquement les adherent_nul
        facture_adherent_null = []
        for row in adherent_null:
            
            if row.get('id') == None:
                facture_adherent_null.append(row)
        
        df = pd.DataFrame(facture_adherent_null)
        regroupe_non_adherent = df.groupby(['Code_Client', 'Nom_Client' ])[['Montant_HT', 'Montant_TTC']].sum().reset_index()
        regroupe_non_adherent = regroupe_non_adherent.to_dict(orient='records')
        
        #print(regroupe_non_adherent)
        #return JSONResponse(content=regroupé_dicts)
        
        
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
    cron_schedule = os.getenv('CRONTAB_APP_FACTURES')
    cron_schedule2 = os.getenv('CRONTAB_APP_COMMANDES')

    # Initialisation du cron pour l'utilisateur root
    #cron = CronTab(user='root')
    cron = CronTab(user='jimmy')
    cron.remove_all()
    cron.write()

    # Définition de la commande
    job = cron.new(command=f'curl http://0.0.0.0:9898/factures/?xCleAPI={API_KEY_URCOOPA}&nb_jours={API_KEY_JOUR}')
    job2 = cron.new(command=f'curl -X POST http://0.0.0.0:9898/envoyer-commande/')
    job.setall(cron_schedule)
    job2.setall(cron_schedule2)
    cron.write()

    # Lancement du service cron
    #print(f"✅ CRON configuré avec la planification : {cron_schedule1} et {cron_schedule2}")
    print(f"✅ CRON configuré avec la planification factures: {cron_schedule} ")
    print(f"✅ CRON configuré avec la planification commandes: {cron_schedule2} ")
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
