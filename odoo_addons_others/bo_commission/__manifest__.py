# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{

    'name': 'Sales & subscriptions commissions',

    'version': '1.0',

    'category': 'sale',

    'summary': 'Sales & subscriptions commissions',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://wwww.blueorange.com.ar',

    'depends': [

        'others',
        'sale_subscription',
        'sale_commission',
        'l10n_ar_afip_webservices_wsfe',

    ],

    'data': [

        'security/ir.model.access.csv',
        'views/account_invoice_line_agent_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_line_agent_view.xml',
        'views/sale_subscription_view.xml',
        'views/sale_commission_settlement_view.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Sales & subscriptions commissions 
======================================
* Se agregan comisionistas y porcentajes de comision en suscripciones, ventas y facturas.
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
