# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

    'name': 'l10n_ar_point_of_sale',

    'version': '1.1',

    'summary': 'Punto de venta para Argentina',

    'description': """
Modulo encargado de manejar talonarios, puntos de venta y mapeo
entre posiciones fiscales y denominaciones.
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'category': 'Accounting',

    'depends': [
        'l10n_ar_afip_tables',
    ],

    'data': [
        'views/document_book_view.xml',
        'views/pos_ar_view.xml',
        'views/menu.xml',
        'views/account_invoice_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_ui_menu.xml',
        'views/res_company_view.xml',
        'data/document_book_type.xml',
        'data/afip_voucher_type.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: