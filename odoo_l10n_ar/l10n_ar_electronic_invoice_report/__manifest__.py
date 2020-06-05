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

    'name': 'l10n_ar_electronic_invoice_report',

    'version': '1.0',

    'description': 'Reporte para facturación electrónica',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'summary': 'Reporte para facturación electrónica',

    'category': 'Accounting',

    'depends': [

        'l10n_ar_afip_webservices_wsfe',
        #'report_custom_filename' TODO: mirar v10 de este modulo, es para que el reporte tenga el nombre del numero de doc
    ],

    'data': [
        'views/pos_ar.xml',
        'report/account_invoice_report.xml',
        'report/report_electronic_invoice.xml',
        'data/email_template.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
