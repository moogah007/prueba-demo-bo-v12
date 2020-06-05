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

    'name': 'l10n ar automatic perceptions',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Cálculo automático de percepciones para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_ar_perceptions_advance',
    ],

    'data': [
        'views/product_product.xml',
        'views/account_invoice.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Cálculo automático de percepciones para Argentina""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
