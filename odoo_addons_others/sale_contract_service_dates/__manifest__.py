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

    'name': 'Sale contract service dates',

    'version': '1.0',

    'summary': 'Integracion para subscripciones y localizacion Argentina',

    'description': 'Integracion para subscripciones y localizacion Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'category': 'sale',

    'depends': [
        'l10n_ar_sale_contract',
        'l10n_ar_afip_webservices_wsfe',
    ],

    'data': [
        'views/sale_subscription_template_view.xml',
    ],

    'installable': True,

    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
