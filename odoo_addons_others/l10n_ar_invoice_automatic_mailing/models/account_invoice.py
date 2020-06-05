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

from odoo import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_to_send = fields.Boolean(string="Factura a enviar", default=False, copy=False)

    def filter_invoices_to_validate_and_send(self):
        return self.filtered(lambda l: l.type == 'out_invoice' and l.state not in ['open','paid','cancel'])
    
    @api.multi
    def get_invoices_with_pos(self):
        pos_with_templates = self.mapped('pos_ar_id').get_pos_with_mailing_template()
        out_invoices = self.filter_invoices_to_validate_and_send()
        invoices_with_pos = out_invoices.filtered(lambda l: l.pos_ar_id in pos_with_templates)
        return invoices_with_pos

    @api.multi
    def send_invoices_by_email(self):
        invoices = self.env['account.invoice'].search([['invoice_to_send', '=', True]])
        for inv in invoices:
            res = inv.pos_ar_id.invoice_mailing_template_id.send_mail(inv.id)
            if res:
                inv.write({'invoice_to_send': False})

    @api.multi
    def action_invoice_open(self):
        invoices_to_mail = self.get_invoices_with_pos()
        res = super(AccountInvoice, self).action_invoice_open()
        # Filtro las facturas cuyos partners tengan email
        invoices_to_mail.filtered(lambda i: i.partner_id.email).write({'invoice_to_send': True})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
