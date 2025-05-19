import requests
import json
import os
from sql.connexion import recupere_connexion_db
import time

import xmlrpc.client

async def createOdoo(rows: list):
            
    # Paramètres
    url = 'https://sdpmajdb-odoo17-dev-staging-sicalait-20406522.dev.odoo.com/'
    db = 'sdpmajdb-odoo17-dev-staging-sicalait-20406522'
    username = 'info.sdpma@sicalait.fr'
    password = 'nathalia974'
    
    #efface la console
    #clear = lambda: os.system('clear')
    #clear()
    
    # Authentification
    info = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = info.authenticate(db, username, password, {})

    if not uid:
        print("❌ Échec de l'authentification.")
        return

    print(f"✅ Authentification réussie. UID: {uid}")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Récupération du fournisseur URCOOPA
    ids_fournisseur = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [[['name', '=', 'URCOOPA']]],
        {'limit': 1}
    )

    if not ids_fournisseur:
        print("❌ Fournisseur 'URCOOPA' non trouvé.")
        return
    # Id fournisseur 
    print(f"✅ Ids fournisseur -> Odoo  : {ids_fournisseur}")
    partner_id = ids_fournisseur[0]

    name_fournisseur = models.execute_kw(
        db, uid, password,
        'res.partner', 'read',
        [ids_fournisseur],
        {'fields': ['name']}
    )[0]['name']
    # Id fournisseur 
    print(f"✅ Name fournisseur -> Odoo : {name_fournisseur}")
    
    
    # Infos communes à toute la facture
    #Contenu de row avant traitement pour Odoo
    import json
    #print(f"✅ Contenu de Rows avant injection. Rows: {json.dumps(rows, indent=2)}")
    numero_facture = rows[0]['Numero_Facture']
    invoice_date = rows[0]['Date_Facture']
    invoice_date_due = rows[0]['Date_Echeance']

    invoice_lines = []

    # Récupération des lignes produits
    for row in rows:
        
        #code produit
        print(f'✅ Code produit récupérer dans Rows->Facture : {row.get('Code_Produit')}')
        code_produit = row.get('Code_Produit')
        
        time.sleep(0.3)  # ralentis de 1000ms
        supplier_ids = models.execute_kw(
            db, uid, password,
            'product.supplierinfo', 'search',
            [[
                ['product_code', '=', code_produit],
                ['partner_id', '=', partner_id]
            ]],
            {'limit': 1}
        )
        #supplier_ids récupérer
        print(f'✅ Supplier_ids récupérer dans Odoo : {supplier_ids}')

        if not supplier_ids:
            print(f"❌ Produit {code_produit} non trouvé dans supplierinfo.")
            continue
        
        time.sleep(0.3)  # ralentis de 1000ms
        #supplier_data
        supplier_data = models.execute_kw(
            db, uid, password,
            'product.supplierinfo', 'read',
            [supplier_ids],
            {'fields': ['product_tmpl_id']}
        )[0]

        #supplier _data récuperer
        print(f'✅ Supplier_data récupéré -> Odoo : {supplier_data}')

        #product tmpl id recupéré uniquement
        product_tmpl = supplier_data.get('product_tmpl_id')

        #Si product tmpl est False on arrete la boucle et on continue sur l'autre produit
        if not product_tmpl or product_tmpl[0] is False:
            print(f"❌ Produit code dans Facture -> Rows {code_produit} non trouvé dans supplierinfo.")
            continue
        
        tmpl_id = supplier_data['product_tmpl_id'][0]

        time.sleep(0.3)  # ralentis de 1000ms
        product_ids = models.execute_kw(
            db, uid, password,
            'product.product', 'search',
            [[['product_tmpl_id', '=', tmpl_id]]],
            {'limit': 1}
        )
        #supplier_ids récupérer
        print(f'✅ Product_ids récupérer -> Odoo  : {product_ids}')

        if not product_ids:
            print(f"❌ Aucun produit trouvé pour le template {tmpl_id}")
            continue

        product_id = product_ids[0]
        print(f"✅ Produit trouvé pour {code_produit} ➔ ID {product_id} \n\n")

        invoice_lines.append([0, 0, {
            'product_id': product_id,
            'quantity': row['Quantite_Facturee'],
            'price_unit': row['Prix_Unitaire']
        }])

    if not invoice_lines:
        print("❌ Aucune ligne de produit valide à créer. Annulation.")
        return

    # Construction de la facture
    sendAccountMove = {
        "move_type": "in_invoice",
        "partner_id": partner_id,
        "invoice_partner_display_name": name_fournisseur,
        "name": numero_facture,
        "ref": numero_facture,
        "invoice_date": invoice_date,
        "invoice_date_due": invoice_date_due,
        "invoice_line_ids": invoice_lines
    }

    # Debug JSON
    #import json
    print("📦 Facture à envoyer à Odoo :")
    print(json.dumps(sendAccountMove, indent=2))

    # Envoi
    try:
        
        move_id = models.execute_kw(
            db, uid, password,
            'account.move', 'create',
            [sendAccountMove]
        )
        
        print(f"✅ Facture Odoo créée avec ID {move_id} \n\n")
    except xmlrpc.client.Fault as e:
        #Retourne tous les erreur odoo
        #Erreur odoo si facture existe sera retrouné
        print(f"❌ Erreur Odoo : {e.faultString} \n\n")
