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

from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def print_invoice_report(self):
        obj = self.browse(self.env.context.get('active_ids')[0])
        if obj.invoice_id.document_book_type == 'electronic':
            report_name = 'l10n_ar_electronic_invoice_report.action_electronic_invoice'
        else:
            report_name = 'account.account_invoices'
        return self.env.ref(report_name).report_action(obj.invoice_id)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
