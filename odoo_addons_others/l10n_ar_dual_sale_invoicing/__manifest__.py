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

    "name": "Dual Sale Invoicing",

    "summary": """Dual Sale Invoicing""",

    "description": """Dual Sale Invoicing""",

    "author": "BLUEORANGE GROUP S.R.L.",

    "website": "https://www.blueorange.com.ar",

    "category": "",

    "version": "1.1",

    "depends": [

        'others',
        'l10n_ar_afip_webservices_wsfe',
        'sale_stock',

    ],

    "data": [

        'views/sale_order.xml',

    ],

    'post_init_hook': "post_init_hook",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
