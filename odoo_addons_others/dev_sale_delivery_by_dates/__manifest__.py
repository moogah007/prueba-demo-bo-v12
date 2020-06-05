# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    "name": "Sale Delivery by Dates",
    'version': '12.0.1.0',
    'sequence': 1,
    "category": 'Generic Modules/Sales Management',
    "summary": """
                   odoo app will create different delivery order for sale order based on given delivery date on sale order line
        """,
    "description": """
         odoo app will create different delivery order for sale order based on given delivery date on sale order line

delivery by dates , sale delivery , sale delivery dates, sale based on delivery date, sale different delivery, delivery date
Sale Delivery by Dates
create different delivery order for sale order based on given delivery date on sale order line
Delivery Date Scheduler for website
Sales delivery date odoo
How can we schedule sales delivery by dates
How can we schedule sales delivery by dates in odoo
Sale Delivery Schedule
Sale delivery date
Sales delivery by dates 
Sale delivery by dates with odoo app
Sales delivery odoo apps
Sale delivery schedule odoo app
Sale delivery schedule odoo
Odoo Sale Delivery by Dates
Odoo create different delivery order for sale order based on given delivery date on sale order line
Odoo Delivery Date Scheduler for website
Manage Sales Delivery date 
Odoo How can we schedule sales delivery by dates
Odoo Sale Delivery Schedule
Odoo Sale delivery date
Odoo Sales delivery by dates 
Different delivery order for sale order
Odoo Different delivery order for sale order
Easy to use with no configuration
Odoo Easy to use with no configuration
Delivery order manage 
Odoo Delivery Order manage 
Confirm the sale Order 
Odoo Confirm the sale Order 
View delivery order 
Odoo view delivery order 
Delivery order management 
Odoo Delivery order management
         
         
         
    """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    'images': ['images/main_screenshot.png'],
    "depends": ['sale_stock', 'stock', 'sale', 'others'],
    "data": [
        'views/sale_order.xml',
        'views/stock_picking_view.xml',
    ],
    'installable' : True,
	'auto_install' : False,	
	'application' : True,
    "price":29.0,
    "currency":'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
