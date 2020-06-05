# - coding: utf-8 -*-
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

    'name': 'l10n ar secondary currency value',

    'version': '1.0',

    'category': '',

    'summary': 'Valores y costos en moneda secundaria',

    'author': 'BLUEORANGE GROUP S.R.L. (www.blueorange.com.ar) / NEXIT',

    'website': 'nexit.com.uy',

    'depends': [

        'purchase',
        'stock_account',
        'mrp_account',
        'l10n_ar_secondary_currency',

    ],

    'data': [

        'views/product_product.xml',
        'views/product_template.xml',
        'views/stock_quant.xml',
        'report/product_product.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Valores y costos en moneda secundaria""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
