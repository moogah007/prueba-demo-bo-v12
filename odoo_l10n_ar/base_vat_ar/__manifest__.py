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

    'name': 'base_vat_ar',

    'version': '1.1',

    'summary': 'Document type and validation for partners for Argentina',

    'description': 'Document type and validation for partners for Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'category': 'base',

    'depends': [
        'base_vat_prefix'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/res_country_view.xml',
        'views/partner_document_type_view.xml',
        'data/res_country_data.xml',
        'data/res.country.csv',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
