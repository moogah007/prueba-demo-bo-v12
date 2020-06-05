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

    'name': 'l10n_ar_wsafip_partner',

    'version': '1.0',

    'summary': '',

    'description': '',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Account',

    'depends': [
        'l10n_ar_afip_tables',
        'sales_team',
        'l10n_ar_afip_webservices_wsaa',
        'others',
    ],

    'data': [
        'views/res_partner.xml',
        'views/wsfe_configuration_view.xml',
        'wizard/views/partner_data_get_wizard.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
