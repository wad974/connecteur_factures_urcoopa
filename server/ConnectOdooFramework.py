import xmlrpc.client

async def createOdoo(row):

    # Paramètre
    # URL ODOO JCWAD
    url = 'https://sdpmajdb-odoo17-dev-staging-sicalait-20406522.dev.odoo.com/'
    #url = 'https://odoo.jcwad.re'
    db = 'sdpmajdb-odoo17-dev-staging-sicalait-20406522'
    #db = 'test_odoo_17'
    #username = 'woodartdeco974@gmail.com'
    #apiKey=788c811c79c24889b2214559c386e6fa2c0eebb9
    username = 'info.sdpma@sicalait.fr'
    password = 'nathalia974'

    # XML-RPC endpoints
    # authentification
    info = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'.format(url))
    uid = info.authenticate(db, username, password, {})

    # Check if authentication is successful
    if uid:
        print("\n\n Authentification réussi. UID:", uid)

        # Get server version
        version = info.version()
        print("Odoo version:", version)
        
        #on match les produis 
        # 1. on recherche les produits dans odoo qui match avec Code_Produit urcoopa
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # id du fournisseur
        ids_fournisseur = models.execute_kw(
            db, 
            uid, 
            password, 
            'res.partner', 
            'search',
            [[['name', '=', 'URCOOPA']]], 
            {'limit' : 1})
        
        print('✅ IDS_FOURNISSEUR -> ', ids_fournisseur[0])
        partner_id = ids_fournisseur[0]
        
        
        # name du fournisseur
        name_fournisseur = models.execute_kw(
        db, 
        uid, 
        password, 
        'res.partner', 
        'read', 
        [ids_fournisseur], 
        {'fields': ['name', 'country_id', 'comment']})
        
        print('✅ NAME_FOURNISSEUR -> ', name_fournisseur[0].get('name'))
        partner_name = name_fournisseur[0].get('name')
        
        
        # Recherche dans product.supplierinfo
        supplier_ids = models.execute_kw(
            db, uid, password,
            'product.supplierinfo', 
            'search',
            [[
                ['product_code', '=', row.get('Code_Produit')],
                ['partner_id', '=', partner_id]
            ]]
        )
        
        print('Supplier_ids -> ', supplier_ids)
        if not supplier_ids:
            print(f"[{row.get('Numero_Facture')}] Aucun produit fournisseur trouvé pour le code {row.get('Code_Produit')} \n\n")
            return
        
        
        #on match les produis 
        # 2. on recherche les produits dans odoo qui match avec Code_Produit urcoopa
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        produit_ids = models.execute_kw(
            db, 
            uid, 
            password, 
            'product.supplierinfo', 
            'search',
            # on match tous les product_code qui sont égale Code_Produit
            [[['product_code', '=', row.get('Code_Produit')]]], 
            {'limit': 1})
        
        #test que chaque produits match
        print('Produit supplierinfo Id qui match: ', produit_ids)
        
        
        supplier = models.execute_kw(
            db, uid, password,
            'product.supplierinfo', 'read',
            [supplier_ids],
            {'fields': ['product_tmpl_id']}
            )[0]
        
        #test que chaque produits match
        print('Supplier: -> ', supplier)
        print('Supplier product_tmpl_id: -> ', supplier['product_tmpl_id'][0])
        product_tmpl_id = supplier['product_tmpl_id'][0]
        
        # Recherche du produit (product.product) par template
        product_ids = models.execute_kw(
            db, uid, password,
            'product.product', 'search',
            [[['product_tmpl_id', '=', product_tmpl_id]]],
            {'limit': 1}
        )
        print('product.product search: -> ', product_ids)
        produit_id_final = product_ids[0]
        
        
        if not product_ids:
            # si match produit retourne vide
            print("Produit Ids: vide -> Aucun ajout produit \n\n")
            return
        
        # Lecture du produit (pour avoir l'ID)
        product = models.execute_kw(
            db, uid, password,
            'product.product', 'read',
            [product_ids],
            {'fields': ['id', 'default_code']}
        )[0]
        product_id = product['id']
        print('✔️ Produit lu:', product)
        
        # creation pour recuperer les produits des factures
        invoice_lines = []
        
        # Si numéro de facture dans row correspond
        if row.get('Numero_Facture') == row.get('Numero_Facture'):  # toujours vrai -> à corriger si besoin
            print('✅ Numéro facture match, ajout produit_id:', product_id)
            invoice_lines.append([0, 0, {
                "product_id": product_id,
                "quantity": row['Quantite_Facturee'],
                "price_unit": row['Prix_Unitaire']
            }])
        else:
            print("❌ Numéro facture ne correspond pas, aucun ajout de ligne.")
            return
        
        
            
        # ajout suite produits dans json        
        # Construction finale de la facture
        sendAccountMove = {
            "move_type": "in_invoice",
            "partner_id": partner_id,
            "invoice_partner_display_name": partner_name,
            "name": row.get('Numero_Facture'),
            "ref": row.get('Numero_Facture'),
            "invoice_date": row.get('Date_Facture'),
            "invoice_date_due": row.get('Date_Echeance'),
            "invoice_line_ids": invoice_lines
        }
        
        '''      
        #json retravailler pour odoo create odoo
        sendAccountMove = {
            "move_type": "in_invoice", # obligatoire pour facture fournisseur
            "partner_id" : partner_id, #fournisseur urcoopa
            #"partner_id" : 14,
            "invoice_partner_display_name" : partner_name, #Nom client ?
            "name" : row.get('Numero_Facture'),
            "ref" : row.get('Numero_Facture'), # reference de la facture
            "invoice_date" : row.get('Date_Facture'), # date de facturation format '%Y-%m-%d'
            "invoice_date_due" : row.get('Date_Echeance'), # date d'échéance format '%Y-%m-%d'
            
            #"amount_untaxed_signed" : 4678.5,
            #"amount_total_signed" : 4776.75,
            #'partner_credit' : 4776.76,
            #"amount_total_in_currency_signed" : 4776.75,
            "invoice_line_ids": [
                    [0, 0, {
                    "product_id" : produit_id_final, # à faire matcher avec code produits
                    "quantity": row.get('Quantite_Facturee'),
                    "price_unit": row.get('Prix_Unitaire'),
                    #'price_subtotal' : 4678.5,
                    #'price_total' : 4776.75
                    #"account_id": 14  # ID d’un compte comptable valide
                }]
            ]
        }
        '''
        # verification dans sendAccountMove
        print('Produit dans Send.Account.Move:' , sendAccountMove)
        
        
        '''
        # Méthodes d'appel object
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        id = models.execute_kw(
            db, 
            uid, 
            password, 
            'account.move', 
            #'search', 
            #'search_read',
            "create",
            [
                #[] # vide
                sendAccountMove
            ]
            )

        #id
        print('models create. RESULTAT: ', id )
        
        partner = models.execute_kw(
            db, 
            uid, 
            password, 
            'account.move', 
            'read', 
            [[id]],
            {'fields': ['name', 'ref']})
        '''
        '''
        #partner
        for value in partner:
            for key,  data in value.items():
                print(f'Models : {key} \n data : {data} \n')
        '''
        
        
        #print('models read. RESULTAT: ',partner partner)
        print("Enregistrement effectué -> TABLEAU SENDACCOUNTMOVE" ' \n\n\n')
        return
        
    else:
        print("Authentication failed.")
        return
