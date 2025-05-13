import requests
import json
import os
from sql.connexion import recupere_connexion_db

# URL de l'API JSON-RPC d'Odoo
url = 'https://sdpmajdb-odoo17-dev-staging-sicalait-18269676.dev.odoo.com/jsonrpc'
# URL ODOO JCWAD
url =  'https://odoo.jcwad.re/jsonrpc'

#efface la console
clear = lambda: os.system('clear')
clear()

# Paramètres de l'appel JSON-RPC
payload = {
    "jsonrpc": "2.0",
    "params": 
    {
        "service": "object",
        "method": "execute_kw",
        "args": [
        "sdpmajdb-odoo17-dev-staging-sicalait-18269676",  #Base
        143,                                              #code user odoo
        #"c92bdb411b18a5f485236d902bcc0a8b3253f460",       #cle api du user
        #"test_odoo_17", #base TEST
        #2, #code user TEST
        "da6df3e251cf139cacf1623605530cc5df07889f", # APY ODOO TEST PERSO
        #"account.move",                               #nom du model ( table ou vue)
        "account.move",
        "search_read",                                    #méthode 
        [
            #[]#vide
            #[('company_id.id','=','19'),('product_tmpl_id.id','=','202259')]  #filtre
            #[('company_id.id','=','3'),('location_id.id','=','42'),('warehouse_id.id','=','4'),('product_id.id','=','190265')]  #filtre
            #[('sale_order_count','>',0)]
            #[('move_type','=','entry')] #,('company_id','=','3')]
            #[('id','=',603001)]
            [('id', '=', 14)]
        ],
        {   #les options : Liste des champs dans fields, offset, limit, order
            #, "employee_ids", "phone_sanitized", "phone_mobile_search", "fiscal_country_codes", "credit", "debit", "total_invoiced", "currency_id", "property_account_payable_id", "property_account_receivable_id", "ref_company_ids", "siret", "total_due", "total_overdue", "sum_franco", "qty_franco", "is_Freight_Forwarder", "import_incoterm_ids"
            #'fields' : ["property_product_pricelist"]
            #'fields' : ["type", "company_type","email_normalized", "name", "complete_name", "ref", "lang","comment", "category_id", "active", "employee", "function", "city", "state_id", "email", "phone", "mobile", "is_company", "is_public", "industry_id", "company_type", "company_id", "user_ids", "partner_share", "commercial_partner_id", "self", "display_name", "create_uid", "create_date", "write_uid", "write_date", "employee_ids", "phone_sanitized", "phone_mobile_search", "fiscal_country_codes", "credit", "debit", "total_invoiced", "currency_id", "property_account_payable_id", "property_account_receivable_id", "ref_company_ids", "siret", "total_due", "total_overdue", "sum_franco", "qty_franco", "is_Freight_Forwarder", "import_incoterm_ids"], 
            #'fields' : ["sequence_prefix", "sequence_number", "name", "ref", "date", "state", "move_type", "journal_id", "company_id", "line_ids", "payment_id", "statement_line_id", "statement_id", "always_tax_exigible", "suitable_journal_ids", "type_name", "country_code", "attachment_ids", "invoice_line_ids", "invoice_date", "invoice_date_due", "delivery_date", "invoice_payment_term_id", "tax_calculation_rounding_method", "partner_id", "commercial_partner_id", "partner_shipping_id", "partner_bank_id", "fiscal_position_id", "payment_reference", "invoice_has_outstanding", "company_currency_id", "currency_id", "direction_sign", "amount_untaxed", "amount_tax", "amount_total", "amount_residual", "amount_untaxed_signed", "amount_tax_signed", "amount_total_signed", "amount_total_in_currency_signed", "amount_residual_signed", "payment_state", "reversed_entry_id", "reversal_move_id", "invoice_vendor_bill_id", "invoice_partner_display_name", "narration", "is_move_sent", "is_being_sent", "invoice_user_id", "user_id", "invoice_origin", "invoice_incoterm_id", "incoterm_location", "invoice_pdf_report_id", "invoice_filter_type_domain", "bank_partner_id", "tax_country_id", "tax_country_code", "has_reconciled_entries", "partner_credit", "display_name", "create_uid", "create_date", "write_uid", "write_date", "payment_ids", "statement_line_ids", "deferred_move_ids", "deferred_original_move_ids", "deferred_entry_type", "extract_state", "extract_status", "amount_paid", "amount_ecotaxe", "purchase_vendor_bill_id", "purchase_id", "purchase_order_count", "stock_move_id", "pos_order_ids", "pos_payment_ids", "pos_refunded_invoice_ids", "team_id", "asset_id", "asset_remaining_value", "asset_depreciated_value", "asset_number_days", "asset_depreciation_beginning_date", "depreciation_value", "asset_ids", "asset_id_display_name", "count_asset", "draft_asset_exists", "landed_costs_ids", "purchase_order_id", "import_cost_line_id", "import_custom_duties_id"] , 
            #'fields': ["id","model", "name", "modules"], #juste les colonnes qu'on a besoin
            #'limit' : 10,
            #'order' : 'detailed_type, list_price asc'

        }
        ],
        "context": {}
    }
}

# En-têtes de la requête
headers = {'Content-Type': 'application/json'}

# Envoi de la requête POST
response = requests.post(url, data=json.dumps(payload), headers=headers)

#efface la console
clear = lambda: os.system('clear')
clear()

# Traitement de la réponse
if response.status_code == 200:
    result = response.json()
    print( 'resultat search read : ', result['result'])
    
    if "result" in result:
      
      for value in result['result']:
        print(value['name'], ' - ', value['company_id'])
        
    else:
        print("Erreur :", result.get("error", "Réponse inattendue"))
else:
    print(f"Erreur HTTP {response.status_code}: {response.text}")