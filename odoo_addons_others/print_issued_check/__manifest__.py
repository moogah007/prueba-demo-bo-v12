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

    'name': 'Print issued check',

    'version': '1.0',

    'category': 'Accounting',

    'summary': """ Impresion de cheques propios """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_ar_account_check',
        'others',
    ],

    'data': [
        'report/print_issued_check_report.xml',
        'report/report_print_issued_check.xml',
        'views/account_checkbook_view.xml',
        'views/account_payment_view.xml',
        'views/print_check_configuration.xml',
        'data/print_check_configuration_data.xml',
        'security/ir.model.access.csv'
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
IMPRESION DE CHEQUES PROPIOS
============================
* Posibilidad, desde la orden de pago, de imprimir los datos de los cheques propios
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
