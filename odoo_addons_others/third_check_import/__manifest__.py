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

    'name': 'Third Check Import',

    'version': '1.0',

    'category': '',

    'summary': 'Third Check Import',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'l10n_ar_account_check',
        'others',
    ],

    'data': [

        'wizard/views/third_check_import_wizard.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Lets the user import third party checks with no payment.""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
