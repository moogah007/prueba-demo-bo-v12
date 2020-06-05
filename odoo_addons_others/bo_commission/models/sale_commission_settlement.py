# -*- encoding: utf-8 -*-
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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleCommissionSettlement(models.Model):
    _inherit = "sale.commission.settlement"

    name = fields.Char(compute="compute_settlement_name", store=True)

    @api.constrains('agent', 'date_to', 'date_from')
    def check_settlement_duplicate(self):
        for r in self:
            if self.search_count([('id', '!=', r.id), ('state', '!=', 'cancel'), ('agent', '=', r.agent.id),
                                  ('date_to', '=', r.date_to), ('date_from', '=', r.date_from)]):
                raise ValidationError("Ya existe una liquidación para el agente y período dados.")

    @api.depends('agent', 'date_to', 'date_from')
    def compute_settlement_name(self):
        for r in self:
            name = ''
            if r.agent and r.date_from and r.date_to:
                name = r.agent.name + '--' + r.date_from.strftime('%d/%m/%Y') + '--' + r.date_to.strftime('%d/%m/%Y')
            r.name = name

    def _prepare_invoice_line(self, settlement, invoice, product):
        """Se agrega cuenta contable de comisionista para la generación de FC proveedor"""
        vals = super(SaleCommissionSettlement, self)._prepare_invoice_line(settlement, invoice, product)
        if invoice.partner_id.agent_account_id:
            vals['account_id'] = invoice.partner_id.agent_account_id.id
        return vals
    
    @api.depends('lines', 'lines.settled_amount')
    def _compute_total(self):
        for settlement in self:
            settlement.total = sum(line.settled_amount * line.invoice.currency_rate if line.invoice.currency_rate else
                                   line.currency_id._convert(line.settled_amount, settlement.currency_id, 
                                   settlement.company_id, line.invoice.date_invoice) for line in settlement.lines)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
