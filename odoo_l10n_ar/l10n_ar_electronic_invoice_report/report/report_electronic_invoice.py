# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api
from odoo.exceptions import ValidationError


class ReportElectronicInvoice(models.AbstractModel):

    _name = 'report.l10n_ar_electronic_invoice_report.report_electronic_invoice'
    _description = 'Reporte de factura electrónica'
    _table = 'report_electronic_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.invoice'].browse(docids)

        if not self.env.context.get('previsualize_invoices'):
            for doc in docs:
                doc.validate_electronic_invoice_fields()

        docargs = {
            'doc_ids': docids,
            'doc_model': self.env['account.invoice'],
            'docs': docs,
            'previsualize': self.env.context.get('previsualize_invoices')
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
