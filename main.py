from fastapi import FastAPI, HTTPException
import zeep
import json
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import requests
import base64
import datetime
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from sql.models import CRUD

# Chargement des variables d'environnement
load_dotenv()

#Récupération des variables d'environnement
WSDL_URL = os.getenv('MY_URCOOPA_URL')

# Vérification des variables requises
if not all([WSDL_URL]):
    raise ValueError("Toutes les variables d'environnement (MY_RDT_URL et MY_RDT_API_KEY) doivent être définies.")

client = zeep.Client(wsdl=WSDL_URL)  # on crée le client UNE fois

app = FastAPI()

@app.get("/factures/")
async def get_factures(xCleAPI: str, nb_jours: int = 10):
    try:
        response = client.service.Get_Factures_Sicalait(xCleAPI=xCleAPI, NbJours=nb_jours)

        if not response:
            raise HTTPException(status_code=404, detail="Aucune facture trouvée.")

        factures = json.loads(response)
        
        # boucles sur factures pour recuperer les datas json
        for row in factures:
            
            '''
                on recupere les champs nécéssaires pour write dans la base de données
                à creer connexion SQL + fonction create base de données si not 
                et update si déjà present : 
                
                Faire une verification des champs if none ou not
                select sur db
                
                Faire une verication if isExist or not
                If true => update 
                If False => create
                
            datas = {
                "Numero_Facture": row["Numero_Facture"],
                "Type_Facture": row["Type_Facture"],
                "Date_Facture": row["Date_Facture"],
                "Date_Echeance": row["Date_Echeance"]
                }
            '''   
            #await CRUD.create(datas)
            #await CRUD.update(datas)
            

        return {"factures": factures}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de décodage JSON.")
    except zeep.exceptions.Fault as fault:
        raise HTTPException(status_code=500, detail=f"Erreur SOAP : {fault}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9898)
