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

    'name': 'Invoice line lot',

    'version': '1.0',

    'category': '',

    'summary': 'Lotes utilizados en lineas de facturas',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'depends': [
        'others',
        'sale',
        'stock',
    ],

    'data': [

        'views/product_template_view.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Cuando se genera una factura desde una venta y esa venta tiene un remito con lotes, '
                   'en las lineas de factura apareceran los lotes utilizados',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
