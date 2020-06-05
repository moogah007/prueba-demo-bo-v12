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

from odoo import http
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class ElectronicInvoicePortalAccount(PortalAccount):
    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        """ Piso la funcion base para pasarle el reporte de factura electronica si la factura lo es"""
        try:
            invoice_sudo = self._document_check_access('account.invoice', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            report = 'account.account_invoices' if invoice_sudo.document_book_type == 'preprint' else \
                'l10n_ar_electronic_invoice_report.action_electronic_invoice'
            context = request.env.context.copy()
            context.update({'previsualize_invoices': True})
            request.env.context = context
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref=report, download=download)

        return super(ElectronicInvoicePortalAccount, self).portal_my_invoice_detail(invoice_id, access_token, report_type, download, **kw)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: