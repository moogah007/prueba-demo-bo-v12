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

    'name': 'l10n_ar_account_check_sale',

    'version': '1.0',

    'summary': 'Venta de cheques de terceros',

    'description': """
Cheques
==================================
    Venta de cheques de terceros.
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'category': 'Accounting',

    'depends': [
        'l10n_ar_account_check',
    ],

    'data': [
        'data/sold_check_data.xml',
        'views/account_third_check_view.xml',
        'views/account_sold_check_view.xml',
        'wizard/wizard_sell_check_view.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'active': False,

    'application': True,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
